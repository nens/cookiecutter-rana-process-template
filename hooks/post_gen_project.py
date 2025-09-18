from pathlib import Path


def print_instructions():
    """This hook is executed inside the generated directory."""
    generated_dir = str(Path(".").absolute())
    print()
    print("Hurray!!! Your rana process project has been created.")
    print()
    print(
        "To get started, open the this project in VScode (or another IDE) follow the README.md for next steps."
    )
    print()
    print(f" > code {generated_dir}")
    print()


if __name__ == "__main__":
    print_instructions()
