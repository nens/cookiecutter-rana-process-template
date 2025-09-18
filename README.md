# Cookiecutter template for N&S Rana processes

Quickstart:

> `cookiecutter https://github.com/nens/cookiecutter-rana-process-template`

To use the template, do not clone this repository!

This repository `cookiecutter-rana-process-template` provides a Cookiecutter ([www.cookiecutter.io](https://www.cookiecutter.io/)) template to generate a fresh Rana process project from a template.
The advantage: easy to start and a similar structure for every project.

First make sure you have Cookiecutter installed before using the template, see >> [Installing Cookiecutter](#installing-cookiecutter).

## Using the template

You initiate the template by call cookiecutter with the URL of this GitHub repository.
It will ask for a project name, these requirements apply: the name should be lowercase only, start with `rana-process-`, use dashes, no underscores.
For example something like `rana-process-flater-sync`.

Open the terminal (for Windows, search "Anaconda Prompt" from start menu).
and navigate to a directory of choice and run the following command:

Using https:
```sh
cookiecutter https://github.com/nens/cookiecutter-rana-process-template
```

Using ssh:
```sh
cookiecutter git@github.com:nens/cookiecutter-rana-process-template
```

(Alternative, if `cookiecutter` is not recognized as a command try `python -m cookiecutter https://github.com/nens/cookiecutter-rana-process-template`.)

After the command, open the the the new directory in VScode (or another IDE).
Then see the ./README.md file for the next steps.

Instructions for the paragraph above will be printed after generating the project, but mentioning it twice won't hurt.

## Installing Cookiecutter

You need to install the cookiecutter program with pip (or pipx).

Use your terminal (for Windows Conda, command-prompt):
```sh
conda install conda-forge::cookiecutter
```

Check the installed version (al least 2.0.0):
```sh
conda run cookiecutter --version
```
