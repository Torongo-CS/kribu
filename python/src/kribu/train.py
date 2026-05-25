## @file train.py
#  @brief Training script for the Sholo Guti supervised learning policy-value model.

import argparse
import numpy as np
import pyarrow.parquet as pq
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from rich.console import Console
from rich.table import Table

import kribu

console = Console()


## @class SholoGutiDataset
#  @brief Custom PyTorch Dataset to load and decode serialized Parquet game states.
class SholoGutiDataset(Dataset):
    ## @brief Initializes the dataset from a Parquet file.
    #  @param parquet_path Path to the Parquet dataset file.
    def __init__(self, parquet_path: str):
        self.table = pq.read_table(parquet_path)
        self.me_col = self.table["me"].to_numpy()
        self.opp_col = self.table["opp"].to_numpy()
        self.cap_col = self.table["activeCaptureIdx"].to_numpy()
        self.policy_col = self.table["policy"].to_pylist()
        self.value_col = self.table["value"].to_numpy()

    ## @brief Returns the total number of samples in the dataset.
    #  @return Total sample count.
    def __len__(self) -> int:
        return len(self.table)

    ## @brief Decodes a single game sample into PyTorch tensors.
    #  @param idx Index of the sample.
    #  @return Tuple of (state_tensor, policy_tensor, value_tensor).
    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        me_val = int(self.me_col[idx])
        opp_val = int(self.opp_col[idx])
        cap_val = int(self.cap_col[idx])
        policy_val = self.policy_col[idx]
        value_val = float(self.value_col[idx])

        bits = np.arange(37, dtype=np.int64)
        me_vec = torch.from_numpy(((me_val >> bits) & 1).astype(np.float32))
        opp_vec = torch.from_numpy(((opp_val >> bits) & 1).astype(np.float32))

        cap_vec = torch.zeros(37, dtype=torch.float32)
        if cap_val != -1:
            cap_vec[cap_val] = 1.0

        state_tensor = torch.stack([me_vec, opp_vec, cap_vec], dim=0)
        policy_tensor = torch.tensor(policy_val, dtype=torch.float32)
        value_tensor = torch.tensor([value_val], dtype=torch.float32)

        return state_tensor, policy_tensor, value_tensor


## @class SholoGutiNet
#  @brief Two-headed policy-value model for predicting moves and win evaluations.
class SholoGutiNet(nn.Module):
    ## @brief Sets up neural network layers (MLP trunk with LayerNorm + residual connection).
    #  @param input_size Input dimension (3 channels x 37 nodes = 111).
    #  @param hidden_size Size of hidden linear layers.
    #  @param num_classes Policy head output dimension (total possible move IDs).
    def __init__(self, input_size: int = 111, hidden_size: int = 256, num_classes: int = kribu.TOTAL_MOVE_COUNT):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.ln1 = nn.LayerNorm(hidden_size)

        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.ln2 = nn.LayerNorm(hidden_size)

        # Policy head
        self.policy_fc = nn.Linear(hidden_size, num_classes)

        # Value head
        self.value_fc1 = nn.Linear(hidden_size, 64)
        self.value_fc2 = nn.Linear(64, 1)

    ## @brief Runs a forward pass.
    #  @param x Input state tensor of shape (batch_size, 3, 37) or (batch_size, 111).
    #  @return Tuple of (policy_logits, value_prediction).
    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        if x.dim() > 2:
            x = x.view(x.size(0), -1)

        h1 = F.relu(self.ln1(self.fc1(x)))
        h2 = F.relu(self.ln2(self.fc2(h1)))

        # Residual skip connection
        h = h1 + h2

        policy_logits = self.policy_fc(h)

        val_h = F.relu(self.value_fc1(h))
        value = torch.tanh(self.value_fc2(val_h))

        return policy_logits, value


## @brief Decodes a board state from integer bitmasks to model input.
#  @param state The board state object.
#  @return Input tensor of shape (1, 3, 37).
def prepare_state_input(state: kribu.boardState) -> torch.Tensor:
    bits = np.arange(37, dtype=np.int64)
    me_vec = torch.from_numpy(((state.me >> bits) & 1).astype(np.float32))
    opp_vec = torch.from_numpy(((state.opp >> bits) & 1).astype(np.float32))

    cap_vec = torch.zeros(37, dtype=torch.float32)
    if state.activeCaptureIdx != -1:
        cap_vec[state.activeCaptureIdx] = 1.0

    return torch.stack([me_vec, opp_vec, cap_vec], dim=0).unsqueeze(0)


## @brief Evaluates a trained model against minimax truth on key test positions.
#  @param model The trained SholoGutiNet.
def evaluate_model_on_test_positions(model: SholoGutiNet) -> None:
    model.eval()

    # Define test positions
    positions = []

    # 1. Initial State
    positions.append(("Initial State", kribu.INITIAL_STATE))

    # 2. State where 'me' has an obvious capture move
    # me at 16, opp at 17, empty at 18
    cap_state = kribu.boardState()
    cap_state.me = 1 << 16
    cap_state.opp = 1 << 17
    cap_state.activeCaptureIdx = -1
    positions.append(("Winning Capture State", cap_state))

    # 3. State where 'me' is blocked and has no moves (losing)
    # Surround 18 completely with opp pieces
    lose_state = kribu.boardState()
    lose_state.me = 1 << 18
    for idx in [12, 13, 14, 17, 19, 22, 23, 24]:
        lose_state.opp |= 1 << idx
    lose_state.opp |= (1 << 16) | (1 << 20) | (1 << 6) | (1 << 8) | (1 << 10) | (1 << 26) | (1 << 28) | (1 << 30)
    lose_state.activeCaptureIdx = -1
    positions.append(("Losing State", lose_state))

    table = Table(title="Model Predictions vs Minimax Ground Truth")
    table.add_column("Position Name", style="cyan")
    table.add_column("Minimax Eval", style="magenta")
    table.add_column("NN Eval (Value Head)", style="magenta")
    table.add_column("Minimax Best Move", style="green")
    table.add_column("NN Predicted Move", style="green")

    with torch.no_grad():
        for name, state in positions:
            # Minimax calculations
            minimax_res = kribu.minimax(state, 4)
            best_score = minimax_res.score
            minimax_move = minimax_res.moveId

            # NN calculations
            inp = prepare_state_input(state)
            policy_logits, value_pred = model(inp)

            # Mask out invalid moves in policy logits to choose the best legal move
            valid_moves = kribu.all_possible_moves(state)
            if valid_moves:
                mask = torch.full_like(policy_logits[0], float("-inf"))
                for m_id in valid_moves:
                    mask[m_id] = 0.0
                masked_logits = policy_logits[0] + mask
                pred_move = int(torch.argmax(masked_logits).item())
            else:
                pred_move = -1

            # Format evaluation display
            val_nn = float(value_pred.item())
            if best_score >= 900000:
                val_mm_str = "Win (1.00)"
            elif best_score <= -900000:
                val_mm_str = "Loss (-1.00)"
            else:
                val_mm_str = f"{best_score / 1600.0:.2f}"

            # Format move display
            if minimax_move == -1:
                mm_move_str = "None"
            elif minimax_move == kribu.END_CHAIN_MOVE:
                mm_move_str = "Pass/End"
            else:
                m = kribu.decode_move(minimax_move)
                mm_move_str = f"{m.fromNode}->{m.toNode}"

            if pred_move == -1:
                nn_move_str = "None"
            elif pred_move == kribu.END_CHAIN_MOVE:
                nn_move_str = "Pass/End"
            else:
                m = kribu.decode_move(pred_move)
                nn_move_str = f"{m.fromNode}->{m.toNode}"

            table.add_row(
                name,
                val_mm_str,
                f"{val_nn:.2f}",
                mm_move_str,
                nn_move_str,
            )

    console.print(table)


## @brief Main training loop.
#  @param dataset_path Path to the Parquet dataset file.
#  @param epochs Number of training epochs.
#  @param batch_size DataLoader batch size.
def train_model(dataset_path: str, epochs: int, batch_size: int) -> None:
    console.print(f"[bold green]Loading dataset from {dataset_path}...[/bold green]")
    dataset = SholoGutiDataset(dataset_path)

    val_size = int(len(dataset) * 0.2)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    console.print(f"Dataset split: {train_size} training, {val_size} validation samples.")

    model = SholoGutiNet()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    console.print("[bold green]Starting model training...[/bold green]")

    for epoch in range(epochs):
        model.train()
        train_policy_loss = 0.0
        train_value_loss = 0.0
        train_samples = 0

        for states, target_policies, target_values in train_loader:
            optimizer.zero_grad()

            pred_policies, pred_values = model(states)

            # Custom cross-entropy for target probability distribution
            log_probs = F.log_softmax(pred_policies, dim=-1)
            policy_loss = -torch.sum(target_policies * log_probs, dim=-1).mean()

            value_loss = F.mse_loss(pred_values, target_values)
            loss = policy_loss + value_loss

            loss.backward()
            optimizer.step()

            batch_size_actual = states.size(0)
            train_policy_loss += policy_loss.item() * batch_size_actual
            train_value_loss += value_loss.item() * batch_size_actual
            train_samples += batch_size_actual

        # Validate
        model.eval()
        val_policy_loss = 0.0
        val_value_loss = 0.0
        val_samples = 0

        with torch.no_grad():
            for states, target_policies, target_values in val_loader:
                pred_policies, pred_values = model(states)

                log_probs = F.log_softmax(pred_policies, dim=-1)
                policy_loss = -torch.sum(target_policies * log_probs, dim=-1).mean()

                value_loss = F.mse_loss(pred_values, target_values)

                batch_size_actual = states.size(0)
                val_policy_loss += policy_loss.item() * batch_size_actual
                val_value_loss += value_loss.item() * batch_size_actual
                val_samples += batch_size_actual

        avg_train_policy = train_policy_loss / train_samples
        avg_train_val = train_value_loss / train_samples
        avg_val_policy = val_policy_loss / val_samples if val_samples > 0 else 0.0
        avg_val_val = val_value_loss / val_samples if val_samples > 0 else 0.0

        console.print(
            f"Epoch {epoch + 1:02d}/{epochs:02d} | "
            f"Train Policy Loss: {avg_train_policy:.4f}, Value Loss: {avg_train_val:.4f} | "
            f"Val Policy Loss: {avg_val_policy:.4f}, Value Loss: {avg_val_val:.4f}"
        )

    # Save model
    model_path = "model.pt"
    torch.save(model.state_dict(), model_path)
    console.print(f"[bold blue]Trained model weights saved to {model_path}[/bold blue]")

    # Run evaluation
    console.print("\n[bold yellow]Evaluating model predictions vs minimax truth:[/bold yellow]")
    evaluate_model_on_test_positions(model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Sholo Guti policy-value neural network.")
    parser.add_argument("--dataset", type=str, default="dataset.parquet", help="Path to Parquet dataset.")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs.")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size for training.")
    args = parser.parse_args()

    train_model(args.dataset, args.epochs, args.batch_size)
