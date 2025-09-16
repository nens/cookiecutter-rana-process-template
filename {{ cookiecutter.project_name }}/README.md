# {{ cookiecutter.project_name }}

In this project you can implement your Rana process workflow, ready to be deployed in our Nelen & Schuurmans Rana platform.
Write your process in the `src/process.py` script, add additional files or modules as needed.
Processes use the RanaSDK package to interact with the platform, handle inputs and outputs, and manage runtime contexts.
See the package documentation [here](https://github.com/nens/ranasdk/) for more information (TODO).

## Development instructions

Sets up the python environment
```sh
conda env create -n {{ cookiecutter.project_name }} --file environment.yml
```

## Local test configuration

Rana processes can be run locally, this requires you to configure a local test runtime.
See `./run_local_test.py`.

// TODO: some instructions to configure the local test runtime.
// - explain purpose of runtime
// - inputs and outputs
// - project_dir function
// - settings in config.yaml

## Running your process locally

Once local test hash been configured, run the local test using your Conda environment.

Once configured, run local test:
```sh
conda run -n {{ cookiecutter.project_name }} python run_local_test.py
```

Alternative, if `conda run` does not work, activate the environment first:
```sh
conda activate {{ cookiecutter.project_name }}
```

```sh
python run_local_test.py
```

## Handy vscode setup: all ready for use

- If you use vscode and did the `uv sync` thingy above, the python plugin will detect   your code and prefect. So you'll have proper code completion! And type hints become more useful. (**Note**: you should have called `uv sync` first, before starting vscode, otherwise you have to select the python version manually: `.venv/bin/python` or so).
- Vscode will **recommend** "python", "editorconfig" and "ruff" extensions: install them. Vscode will ask about trusting "editorconfig" and "astral software": yes, that's okay. - Editorconfig handles unneeded spaces at the end of lines and other minutia.
- Ruff formats your code and sorts the imports whenever you save a file. It will also warn about unknown variables or unused imports and offer fixes.
- The "run and debug" button in the activity bar runs `src/flows.py` against localhost:4200 if you select "{{ cookiecutter.__debug_action_name }}" in the dropdown. See the instructions in `src/flows.py` on how to use it.

Nice, easy, modern development with mostly-automatic formatting and neatness!


## Upload your project to GitHub

If you finish your Rana process project and would like to you can share it on GitHub.
First, use the following url to create a new empty repo on GitHub ('Empty' means no readme, .gitignore or license):

> [https://github.com/new?name={{ cookiecutter.project_name }}&owner=nens&visibility=private&description=Rana+process](https://github.com/new?name={{ cookiecutter.project_name }}&owner=nens&visibility=private&description=Rana+process)

Done? Go to your generated project and do some git magic:

- Open terminal and go to your Rana process:
```sh
cd {current_dir}
```

- Initialize a new git repository:
```sh
git init
```

- Add all files:
```sh
git add -A
```

- Commit the files:
```sh
git commit -m "Generated with cookiecutter"
```

- Set the main branch to `main` (not `master`):
```sh
git branch -M main
```

- Add the remote repository (choose https or ssh):
```sh
git remote add origin https://github.com/nens/{{ cookiecutter.project_name }}.git
```

- Or for ssh:
```sh
git remote add origin git@github.com:nens/{{ cookiecutter.project_name }}.git
```

- Push the code to GitHub:
```sh
git push origin
```

- Go to the ["manage access" page](https://github.com/nens/{{ cookiecutter.project_name }}/settings/access) and click "add teams": add the "adviseurs" add "programeurs" team with at least **read** access.

- Lastly, share your project using the following URL: [https://github.com/nens/{{ cookiecutter.project_name }}](https://github.com/nens/{{ cookiecutter.project_name }})
