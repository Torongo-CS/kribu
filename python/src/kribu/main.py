"""
Simulation script demonstrating the Kribu Sholo Guti engine functionality.
"""

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# pyrefly: ignore [missing-import]
import kribu_ext as kribu


def render_board(state: kribu.boardState) -> str:
    """
    Renders the boardState as a colorized ASCII board layout.
    """

    def char(nodeId):
        isMe = (state.me & (1 << nodeId)) != 0
        isOpp = (state.opp & (1 << nodeId)) != 0
        if isMe:
            return "[bold green]M[/bold green]"
        if isOpp:
            return "[bold red]O[/bold red]"
        if state.activeCaptureIdx == nodeId:
            return "[bold yellow]*[/bold yellow]"
        return "[grey50].[/grey50]"

    c = [char(i) for i in range(37)]

    # We lay out the nodes precisely using a formatted string template
    boardStr = f"""
   {c[0]}───────────────{c[1]}───────────────{c[2]}
     ╲             │             ╱
       ╲           │           ╱
         ╲         │         ╱
           {c[3]}───────{c[4]}───────{c[5]}
             ╲      │      ╱
               ╲    │    ╱
                 ╲  │  ╱
   {c[6]}───────{c[7]}───────{c[8]}───────{c[9]}───────{c[10]}
   │ ╲     │     ╱ │ ╲     │     ╱ │
   │   ╲   │   ╱   │   ╲   │   ╱   │
   │     ╲ │ ╱     │     ╲ │ ╱     │
   {c[11]}───────{c[12]}───────{c[13]}───────{c[14]}───────{c[15]}
   │     ╱ │ ╲     │     ╱ │ ╲     │
   │   ╱   │   ╲   │   ╱   │   ╲   │
   │ ╱     │     ╲ │ ╱     │     ╲ │
   {c[16]}───────{c[17]}───────{c[18]}───────{c[19]}───────{c[20]}
   │ ╲     │     ╱ │ ╲     │     ╱ │
   │   ╲   │   ╱   │   ╲   │   ╱   │
   │     ╲ │ ╱     │     ╲ │ ╱     │
   {c[21]}───────{c[22]}───────{c[23]}───────{c[24]}───────{c[25]}
   │     ╱ │ ╲     │     ╱ │ ╲     │
   │   ╱   │   ╲   │   ╱   │   ╲   │
   │ ╱     │     ╲ │ ╱     │     ╲ │
   {c[26]}───────{c[27]}───────{c[28]}───────{c[29]}───────{c[30]}
                 ╱  │  ╲
               ╱    │    ╲
             ╱      │      ╲
           {c[31]}───────{c[32]}───────{c[33]}
         ╱          │         ╲
       ╱            │           ╲
     ╱              │             ╲
    {c[34]}───────────────{c[35]}───────────────{c[36]}
    """
    return boardStr


def main():
    """
    Main simulation function demonstrating board states, move generation, and capture chains.
    """
    console = Console()

    # Title Banner
    console.print("\n")
    console.print(
        Panel(
            Text("KRIBU - SHOLO GUTI ENGINE SIMULATION", style="bold cyan", justify="center"),
            subtitle="Coordinate-Free Declarative Compile-Time Rule Engine",
            box=box.DOUBLE,
            border_style="cyan",
        )
    )
    console.print("\n")

    # 1. Structural/Compile-time tables metadata
    metaTable = Table(title="Board Structural Statistics", box=box.ROUNDED, border_style="blue")
    metaTable.add_column("Property", style="bold magenta")
    metaTable.add_column("Value", style="green")
    metaTable.add_row("Total Nodes", f"{kribu.NUM_NODES}")
    metaTable.add_row("Simple Moves Count", f"{kribu.NUM_SIMPLE_MOVES}")
    metaTable.add_row("Capture Moves Count)", f"{kribu.NUM_CAPTURE_MOVES}")
    metaTable.add_row("Total Moves (Including End-Chain)", f"{kribu.TOTAL_MOVE_COUNT}")
    console.print(metaTable)
    console.print("\n")

    # 2. Show all decoded moves to illustrate the stability and layout
    console.print("[bold yellow]Decoded Move Table (All Simple & Capture Moves):[/bold yellow]")
    sampleTable = Table(box=box.SIMPLE, header_style="bold blue")
    sampleTable.add_column("Move ID", justify="right")
    sampleTable.add_column("Type")
    sampleTable.add_column("From Node")
    sampleTable.add_column("To Node")
    sampleTable.add_column("Captured Node")

    # All simple moves
    for i in range(1, kribu.NUM_SIMPLE_MOVES + 1):
        m = kribu.decode_move(i)
        sampleTable.add_row(f"{i}", "Simple", f"{m.fromNode}", f"{m.toNode}", "-")

    # All capture moves
    startCapture = kribu.NUM_SIMPLE_MOVES + 1
    for i in range(startCapture, kribu.TOTAL_MOVE_COUNT):
        m = kribu.decode_move(i)
        sampleTable.add_row(f"{i}", "Capture", f"{m.fromNode}", f"{m.toNode}", f"{m.captured}")

    console.print(sampleTable)
    console.print("\n")

    # 3. Simulate Initial State
    console.print(Panel(Text("Simulating Code Run & Functions", style="bold green"), box=box.ROUNDED))

    state = kribu.INITIAL_STATE
    console.print("[bold cyan]1. Initial Board State (`INITIAL_STATE`):[/bold cyan]")
    console.print(
        f"Me Piece Count: [green]{kribu.piece_count(state.me)}[/green], Opponent Piece Count: [red]{kribu.piece_count(state.opp)}[/red]"
    )
    console.print(render_board(state))
    console.print("\n")

    # 4. Generate & Display possible moves from initial state
    moves = kribu.all_possible_moves(state)
    console.print(
        "[bold cyan]2. Generating all possible moves from Initial State (`all_possible_moves()`):[/bold cyan]"
    )
    console.print(f"Total valid moves available: [green]{len(moves)}[/green]")
    console.print(f"Sample available move IDs: {moves[:10]}...")
    console.print("\n")

    # 5. Apply a normal move (e.g. Me moves 21 to 16)
    # Let's find the move ID
    moveId = -1
    for mId in moves:
        m = kribu.decode_move(mId)
        if m.fromNode == 21 and m.toNode == 16:
            moveId = mId
            break

    if moveId != -1:
        console.print(f"[bold cyan]3. Applying move 21 -> 16 (Move ID {moveId}) via `apply_move()`:[/bold cyan]")
        state = kribu.apply_move(state, moveId)
        console.print(
            f"Me Piece Count: [green]{kribu.piece_count(state.me)}[/green], Opponent Piece Count: [red]{kribu.piece_count(state.opp)}[/red]"
        )
        console.print(render_board(state))
        console.print("\n")

    # 6. Show board flipping (flip_board)
    console.print("[bold cyan]4. Rotating board 180 degrees (`flip_board()`):[/bold cyan]")
    console.print("This flips the board, mapping nodes symmetrically, and swaps active player (Me) and opponent (Opp).")
    flipped = kribu.flip_board(state)
    console.print("Flipped Board State (Me is now the former Opponent):")
    console.print(
        f"Me Piece Count: [green]{kribu.piece_count(flipped.me)}[/green], Opponent Piece Count: [red]{kribu.piece_count(flipped.opp)}[/red]"
    )
    console.print(render_board(flipped))
    console.print("\n")

    # 7. Setup and simulate a multi-capture chain!
    console.print(Panel(Text("Simulating Multi-Capture Chaining Scenario", style="bold green"), box=box.ROUNDED))

    # Custom scenario:
    # Me piece at node 16.
    # Opponent pieces at 17 and 19.
    # Node 18 and 20 are empty.
    chainState = kribu.boardState()
    chainState.me = 1 << 16
    chainState.opp = (1 << 17) | (1 << 19)
    chainState.activeCaptureIdx = -1

    console.print("[bold cyan]Custom Board Setup for Capture Chain:[/bold cyan]")
    console.print("Me piece at node 16. Opponent pieces at nodes 17 and 19.")
    console.print(render_board(chainState))
    console.print("\n")

    # Possible moves from chainState
    chainMoves = kribu.all_possible_moves(chainState)
    console.print(f"Available Move IDs from setup: {chainMoves}")
    for mId in chainMoves:
        m = kribu.decode_move(mId)
        console.print(f"  - Move ID {mId}: {m.fromNode} -> {m.toNode} (Capture {m.captured})")

    # Find the move ID for 16 -> 18 (capturing 17)
    cap1Id = -1
    for mId in chainMoves:
        m = kribu.decode_move(mId)
        if m.fromNode == 16 and m.toNode == 18:
            cap1Id = mId
            break

    if cap1Id != -1:
        console.print(f"\n[bold cyan]Applying first capture (16 -> 18, Move ID {cap1Id}):[/bold cyan]")
        chainState = kribu.apply_move(chainState, cap1Id)
        console.print(
            f"Active Capture Index: [yellow]{chainState.activeCaptureIdx}[/yellow] "
            "(Piece is locked at node 18 for multi-capture)"
        )
        console.print(render_board(chainState))
        console.print("\n")

        # Next moves (should include END_CHAIN_MOVE and the next capture)
        nextMoves = kribu.all_possible_moves(chainState)
        console.print(f"Available Move IDs in chain: {nextMoves}")
        for mId in nextMoves:
            if mId == kribu.END_CHAIN_MOVE:
                console.print(f"  - Move ID {mId}: END_CHAIN_MOVE (Stop capturing and end turn)")
            else:
                m = kribu.decode_move(mId)
                console.print(f"  - Move ID {mId}: {m.fromNode} -> {m.toNode} (Capture {m.captured})")

        # Find the next capture move ID (18 -> 20, capturing 19)
        cap2Id = -1
        for mId in nextMoves:
            if mId != kribu.END_CHAIN_MOVE:
                m = kribu.decode_move(mId)
                if m.fromNode == 18 and m.toNode == 20:
                    cap2Id = mId
                    break

        if cap2Id != -1:
            console.print(f"\n[bold cyan]Applying second capture (18 -> 20, Move ID {cap2Id}):[/bold cyan]")
            chainState = kribu.apply_move(chainState, cap2Id)
            console.print(
                f"Active Capture Index: [yellow]{chainState.activeCaptureIdx}[/yellow] "
                "(-1 means chain has automatically ended as no further captures are possible)"
            )
            console.print(render_board(chainState))
            console.print("\n")

    # 8. Check Game Over / Winner
    console.print(Panel(Text("Game Over & Win Condition Verification", style="bold green"), box=box.ROUNDED))
    status = kribu.get_game_status(chainState)
    isGameOver = status != kribu.GameStatus.ONGOING
    console.print(f"Is game over on capture chain board? [green]{isGameOver}[/green]")
    winnerStr = (
        "Me"
        if status == kribu.GameStatus.ME_WINS
        else "Opponent"
        if status == kribu.GameStatus.OPP_WINS
        else "No one (game not over)"
    )
    console.print(f"Winner: [bold green]{winnerStr}[/bold green]")
    console.print("\n")


if __name__ == "__main__":
    main()
