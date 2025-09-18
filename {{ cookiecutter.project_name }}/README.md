# {{ cookiecutter.project_name }}

In this project you can implement your Rana process workflow, ready to be deployed in our Nelen & Schuurmans Rana platform.
Write your process in the `src/process.py` script and add additional files or modules as needed.
Processes use the RanaSDK package to interact with the platform, handle inputs and outputs, and manage runtime contexts.
See the [rana-process-sdk](https://pypi.org/project/rana-process-sdk/) on PyPI for more information.

## Run process local test

On [https://www.ranawaterintelligence.com/](https://www.ranawaterintelligence.com/) processes rely on an online runtime for inputs, outputs of project files, and interaction with external systems.
The Rana process SDK supports a local test runtime, allowing you to run a process in your own environment.
This allows files to be read and written from your local filesystem, instead of your project on the Rana platform.
See the following instructions how to configure this local runtime and run your process.

#### Configure run local test

The `local_test/` directory contains what is needed to run a local test of your Rana process.
In the `local_test/run.py` file you will find the following code snippet:

```python
runtime = LocalTestRanaRuntime(
    working_dir="local_test/working_dir",
    project_dir="local_test/project_dir",
    settings=get_local_test_settings(),
    cleanup_workdir=True,
)
```

This runtime configuration defines the `working_dir` path, which will be created to hold temporary files during the process run.
Furthermore, the `project_dir` points to a directory used to contain files as if it were a project in Rana.
The `get_local_test_settings()` function reads the `local_test/config.yaml` file containing local test configuration (see next paragraph).
The `cleanup_workdir` flag indicates if the `working_dir` must be removed after the process run (turn off to inspect files after  process execution).

Copy `local_test/placeholder_config.yaml` to `local_test/config.yaml` and adjust it for your local test run, if necessary.
Depending on your process, the most common configuration use cases are authentication with Lizard or 3Di.
Another case is if your process interacts with dataset normally provided in Rana, these would also be configured here.
See [LocalTestSettings](https://github.com/nens/rana-process-sdk/blob/main/src/rana_process_sdk/settings/local_test_settings.py) for all configuration options.
This part of the SDK is still being streamlined, so if you need help, please contact the Rana development team.

#### Define input and output parameters

The following section of the `local_test/run.py` file defines the input and output variables used as process parameters.

```python
inputs = {
    "name": "Pizza cursus"
}

outputs = {}
```

You need to adjust the input and output variables to match the parameter declaration of the process you are developing.

To reference a file in an input parameter definition, use a dictionary with the `id` key to point to a file in the `project_dir`.
```python
inputs = {
    "study_area": {"id": "test_shape_gp_1.gpkg"},
}
```

#### Call the run local test function

Finaly, the process is executed using the `run_local_test()` function.

```python
run_local_test(
    rana_flow=process,
    runtime=runtime,
    inputs=inputs,
    output_paths=outputs,
)
```

The process will then be executed using the provided parameters in the local test runtime configuration.
If the process reads files from the project, make sure they are present in the project directory at `local_test/project_dir`.

#### Run local test

You can run the `local_test/run.py` file once it has been configured in the previous section.

Open Anaconda Command Prompt in your project directory and create a Conda environment using the following command
```sh
conda env create -n {{ cookiecutter.project_name }} --file environment.yml
```

Run the following command to start the local test:
```sh
conda run -n {{ cookiecutter.project_name }} python -m local_test.run
```

Alternatively, if `conda run` does not work, activate the environment first:
```sh
conda activate {{ cookiecutter.project_name }}
```
Then execute:

```sh
python -m local_test.run
```

## Upload your project to GitHub

If you finish your Rana process project and would like to, you can share it on GitHub.
First, use the following url to create a new empty repo on GitHub ('Empty' means no readme, .gitignore or license):

> [https://github.com/new?name={{ cookiecutter.project_name }}&owner=nens&visibility=private&description=Rana+process](https://github.com/new?name={{ cookiecutter.project_name }}&owner=nens&visibility=private&description=Rana+process)

Once done, go to your generated project and run the following git commands:

- Open terminal for your Rana process and initialize a new git repository:
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

- Go to the ["manage access" page](https://github.com/nens/{{ cookiecutter.project_name }}/settings/access) and click "add teams": add the "adviseurs" and "programeurs" teams with at least **read** access.

- Lastly, share your project using the following URL: [https://github.com/nens/{{ cookiecutter.project_name }}](https://github.com/nens/{{ cookiecutter.project_name }})
