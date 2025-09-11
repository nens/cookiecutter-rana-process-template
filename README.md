# Cookiecutter template for N&S Rana processes

**Want to use this template? Do not clone this repository!**

This repository `cookiecutter-rana-process-template` provides a Cookiecutter ([www.cookiecutter.io](https://www.cookiecutter.io/)) template to generate a fresh Rana project from a template.
The advantage: easy to start and a similar structure for every project.

First make sure you have Cookiecutter installed before using the template.

## Installing Cookiecutter

You need to install the cookiecutter program with pip (or pipx).

Use your terminal (for Windows Conda, command-prompt):
```sh
pip install cookiecutter
```

Alternative uv:
```sh
uv tool install cookiecutter
```

Check the installed version (al least 2.0.0):
```sh
cookiecutter --version
```

## Using the template

You initiate the template by call cookiecutter with the URL of this GitHub repository.

It will ask for a project name:

- Lowercase only, please.
- Start with `rana-process-`.
- Dashes, no underscores.
- So something like `rana-process-flater-sync`.

Open the terminal (for Windows Conda, command-prompt) and navigate to a directory of choice and run the following command:

Using https:
```sh
cookiecutter https://github.com/nens/cookiecutter-rana-process-template
```

Using ssh:
```sh
cookiecutter git@github.com:nens/cookiecutter-rana-process-template
```

(Alternative, you might need to use `python -m cookiecutter` if `cookiecutter` is not recognized as a command.)

After the command, open the the the new directory in VScode (or another IDE).
Then see the ./README.md file for the next steps.

Instructions for the paragraph above will be printed after generating the project, but mentioning it twice won't hurt.

## Development on this template

The regular:

```sh
uv venv
```

```sh
source .venv/bin/activate
```

```sh
uv pip install -r requirements.txt
```

```sh
pytest
```
