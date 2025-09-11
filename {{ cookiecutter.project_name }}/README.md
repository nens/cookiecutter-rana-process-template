# {{ cookiecutter.project_name }}

TODO: add a description or documentation of your code here, what the aim is, etc.

If you have worked on other rana processes or Prefect projects, you probably have these two installed already:

## Development instructions

Sets up the python environment
```sh
conda env create -n {{ cookiecutter.project_name }} -f environment.yml
```

Run the local test:
```sh
conda run -n {{ cookiecutter.project_name }} python run_local_test.py
```

Write your process in the `src` folder, with your 'main' script in `process.py`.
Feel free to add new folders or files in the `src` folder.

## Running your process locally

You can run your process through configuration of a local test environment. This is done in `run_process.py`.

```sh
```


## Handy vscode setup: all ready for use

- If you use vscode and did the `uv sync` thingy above, the python plugin will detect   your code and prefect. So you'll have proper code completion! And type hints become more useful. (**Note**: you should have called `uv sync` first, before starting vscode, otherwise you have to select the python version manually: `.venv/bin/python` or so).
- Vscode will **recommend** "python", "editorconfig" and "ruff" extensions: install them. Vscode will ask about trusting "editorconfig" and "astral software": yes, that's okay. - Editorconfig handles unneeded spaces at the end of lines and other minutia.
- Ruff formats your code and sorts the imports whenever you save a file. It will also warn about unknown variables or unused imports and offer fixes.
- The "run and debug" button in the activity bar runs `src/flows.py` against localhost:4200 if you select "{{ cookiecutter.__debug_action_name }}" in the dropdown. See the instructions in `src/flows.py` on how to use it.

Nice, easy, modern development with mostly-automatic formatting and neatness!


## Upload your project to github

First, use the following url to create a new empty repo on github.
'Empty' means don't let github generate a readme, .gitignore or license, the cookiecutter already provides them to you.

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
git push origin")
```

- Go to the ["manage access" page](https://github.com/nens/{{ cookiecutter.project_name }}/settings/access) and click "add teams": add the "adviseurs" add "programeurs" team with at least **read** access.

- Lastly, share your project using the following URL: [https://github.com/nens/{{ cookiecutter.project_name }}](https://github.com/nens/{{ cookiecutter.project_name }})


## Deploying your flow to production

On every commit to the `main` branch, a new docker image is generated on github *if pre-commit doesn't complain* and *if the docker image can be build*. The server looks for new images every five minutes and downloads+restarts it automatically.

Should the github action complain about pre-commit, upgrade the config and run it again:

    $ pre-commit autoupdate
    $ pre-commit run --all

Should the github action fail on the docker image creation, try that one out locally and fix any errors:

    $ docker build .

Initially, ask Taj or Reinout to add your new deployment to the [prefect-setup repo](https://github.com/nens/prefect-setup/blob/main/docker-compose.task.yml)_.
