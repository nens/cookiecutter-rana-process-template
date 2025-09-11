from pathlib import Path

PROJECT_NAME = "{{ cookiecutter.project_name }}"


def print_instructions(project_name: str = PROJECT_NAME):
    """This hook is executed inside the generated directory."""
    generated_dir = str(Path(".").absolute())
    print()
    print("Hurray!!! Your rana process project has been created.")
    print()
    print("Project location:", generated_dir)
    print()
    print("To get started, open the the this project in VScode (or another IDE)")
    print("See the README.md in the project for the next steps.")
    print()
    print(f" > {generated_dir}/README.md")
    print()


if __name__ == "__main__":
    print_instructions()
