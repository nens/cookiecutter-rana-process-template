# {{ cookiecutter.project_name }} Rana process

## Post-generation checklist

If you have worked on other rana processes or Prefect projects, you probably have these two installed already:

- [ ] To make it easy for Windows user to install GDAL we use `conda`. It handles the virtualenv, the pip install, and pinning versions. You need to install it, [here are the instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).
- [ ] Run `uv sync`.
- [ ] To keep the code readable and maintainable, we use pre-commit. Install it with `pip install pre-commit` .
- [ ] Set up pre-commit to automatically run before every commit: `pre-commit install` .

Lastly a bit of readme cleanup:

- [ ] In the next section, quickly add an initial sentence about the project.
- [ ] Remove this whole post-generation checklist from the readme. You won't need it anymore as you've diligently checked off every item :-)

Necessary Github administration if you want to share your code with others:

- [ ] Just making sure: you created a github repo and did the init/add/push shown after generating the project?
- [ ] Go to the ["manage access" page](https://github.com/nens/{{ cookiecutter.project_name }}/settings/access) and click "add teams": add the "adviseurs" add "programeurs" team with **write** access. Otherwise you're the only one who can work on it.



## Rana process documentation

TODO: add the documentation of your code here, what the aim is, etc.


## Development instructions

Sets up the python environment
```sh
conda create -n {{ cookiecutter.project_name }} python=3.12
```

Activate conda environment
```sh
conda activate {{ cookiecutter.project_name }}
```

Install Python requirements
```sh
conda install --yes --file requirements.txt
```

Intall GDAL through conda-forge
```sh
conda install -c conda-forge gdal
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


## Deploying your flow to production

On every commit to the `main` branch, a new docker image is generated on github *if pre-commit doesn't complain* and *if the docker image can be build*. The server looks for new images every five minutes and downloads+restarts it automatically.

Should the github action complain about pre-commit, upgrade the config and run it again:

    $ pre-commit autoupdate
    $ pre-commit run --all

Should the github action fail on the docker image creation, try that one out locally and fix any errors:

    $ docker build .

Initially, ask Taj or Reinout to add your new deployment to the [prefect-setup repo](https://github.com/nens/prefect-setup/blob/main/docker-compose.task.yml)_.
