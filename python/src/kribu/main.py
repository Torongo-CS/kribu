# pyrefly: ignore [missing-import]
from kribu import is_prime
from rich.console import Console


def main():
    console = Console()
    console.print("[bold green]Kribu Python Wrapper Initialized![/bold green]")

    # Test the C++ binding
    test_val = 1000000007
    console.print(f"Checking if {test_val} is prime via C++ engine...")

    result = is_prime(test_val)
    if result:
        console.print(f"[bold cyan]{test_val} is PRIME![/bold cyan]")
    else:
        console.print(f"[bold red]{test_val} is NOT PRIME.[/bold red]")


if __name__ == "__main__":
    main()
