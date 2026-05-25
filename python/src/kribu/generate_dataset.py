## @file generate_dataset.py
#  @brief Dataset generator simulating Sholo Guti games using C++ minimax.

import argparse
import concurrent.futures
import random
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from rich.console import Console
from rich.progress import Progress

import kribu

console = Console()


## @brief Simulates a single game of Sholo Guti and records samples.
#  @param minimax_depth Search depth for minimax evaluation.
#  @return List of sample dictionaries containing board representation, policy, and value.
def generate_game(minimax_depth: int = 4) -> list[dict]:
    samples = []
    state = kribu.INITIAL_STATE
    ply_count = 0
    max_plies = 200

    # Decide opening random length
    random_plies = random.randint(4, 6)
    use_random_opening = random.random() < 0.5

    while ply_count < max_plies:
        status = kribu.get_game_status(state)
        if status != kribu.GameStatus.ONGOING:
            break

        moves = kribu.all_possible_moves(state)
        if not moves:
            break

        # Evaluate each move
        move_scores = []
        for m_id in moves:
            next_state = kribu.apply_move(state, m_id)
            if next_state.activeCaptureIdx == -1:
                flipped = kribu.flip_board(next_state)
                res = kribu.minimax(flipped, minimax_depth)
                score = -res.score
            else:
                res = kribu.minimax(next_state, minimax_depth)
                score = res.score
            move_scores.append(score)

        # Scale/normalize scores for softmax stability
        scaled_scores = []
        for s in move_scores:
            if s >= 900000:
                scaled_scores.append(20.0)
            elif s <= -900000:
                scaled_scores.append(-20.0)
            else:
                scaled_scores.append(s / 100.0)

        # Determine temperature based on ply count
        if ply_count < 8:
            temp = 1.5
        elif ply_count < 20:
            temp = 0.8
        else:
            temp = 0.2

        if use_random_opening and ply_count < random_plies:
            probs = np.ones(len(moves)) / len(moves)
        else:
            logits = np.array(scaled_scores, dtype=np.float64) / temp
            logits -= np.max(logits)  # numerical stability
            exp_logits = np.exp(logits)
            probs = exp_logits / np.sum(exp_logits)

        # Policy target vector: probability distribution over all move IDs
        policy_vector = np.zeros(kribu.TOTAL_MOVE_COUNT, dtype=np.float32)
        for idx, m_id in enumerate(moves):
            policy_vector[m_id] = probs[idx]

        # Value target: minimax score of the best move, normalized to [-1, 1]
        best_score = max(move_scores)
        if best_score >= 900000:
            value_target = 1.0
        elif best_score <= -900000:
            value_target = -1.0
        else:
            value_target = best_score / 1600.0  # max difference is 16 pieces * 100 = 1600

        samples.append(
            {
                "me": int(state.me),
                "opp": int(state.opp),
                "activeCaptureIdx": int(state.activeCaptureIdx),
                "policy": policy_vector.tolist(),
                "value": float(value_target),
            }
        )

        # Sample and apply move
        chosen_move = random.choices(moves, weights=probs, k=1)[0]
        state = kribu.apply_move(state, chosen_move)

        if state.activeCaptureIdx == -1:
            state = kribu.flip_board(state)

        ply_count += 1

    return samples


## @brief Simulates multiple games in parallel and saves them as a Parquet file.
#  @param num_games Number of self-play games to simulate.
#  @param output_path File path to save the Parquet dataset.
#  @param minimax_depth Search depth for minimax evaluation.
def generate_dataset(num_games: int, output_path: str, minimax_depth: int = 4) -> None:
    all_samples = []

    console.print(f"[bold green]Starting simulation of {num_games} games (depth {minimax_depth})...[/bold green]")

    with Progress() as progress:
        task = progress.add_task("[cyan]Simulating games...", total=num_games)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(generate_game, minimax_depth) for _ in range(num_games)]
            for future in concurrent.futures.as_completed(futures):
                all_samples.extend(future.result())
                progress.advance(task)

    console.print(f"[bold green]Simulation complete. Total samples generated: {len(all_samples)}[/bold green]")

    # Convert samples to pyarrow Table
    me_arr = pa.array([s["me"] for s in all_samples], type=pa.int64())
    opp_arr = pa.array([s["opp"] for s in all_samples], type=pa.int64())
    cap_arr = pa.array([s["activeCaptureIdx"] for s in all_samples], type=pa.int16())
    poly_arr = pa.array([s["policy"] for s in all_samples], type=pa.list_(pa.float32()))
    val_arr = pa.array([s["value"] for s in all_samples], type=pa.float32())

    table = pa.Table.from_arrays(
        [me_arr, opp_arr, cap_arr, poly_arr, val_arr],
        names=["me", "opp", "activeCaptureIdx", "policy", "value"],
    )

    pq.write_table(table, output_path)
    console.print(f"[bold blue]Saved dataset to {output_path}[/bold blue]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Sholo Guti self-play dataset using minimax.")
    parser.add_argument("--games", type=int, default=100, help="Number of games to simulate.")
    parser.add_argument("--output", type=str, default="dataset.parquet", help="Output Parquet file path.")
    parser.add_argument("--depth", type=int, default=4, help="Minimax search depth.")
    args = parser.parse_args()

    generate_dataset(args.games, args.output, args.depth)
