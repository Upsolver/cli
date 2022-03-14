# Upsolver CLI
The Upsolver Command Line Interface.

![example workflow](https://github.com/Upsolver/cli/actions/workflows/run-tests.yaml/badge.svg)
![example workflow](https://github.com/Upsolver/cli/actions/workflows/static-checks.yaml/badge.svg)

## Installation

### MacOS

```commandline
brew tap Upsolver/cli
brew install upsolver-cli
```

### Windows
Install using `pip` (Python 3.10+ required):

```commandline
pip install https://github.com/Upsolver/cli/releases/download/v0.1.0/cli-0.1.0.tar.gz --user
```

You can grab the latest archive link from https://github.com/Upsolver/cli/releases

## Usage

### Login
First, you'll need to login:
```commandline
upsolver login
```

By default, this will attempt to use `https://api.upsolver.com` endpoint; if you wish to use a different API endpoint, specify it with:

```commandline
upsolver login --base-url https://localhost:8080
```

### Configure
You can edit `~/.upsolver/config` manually, or use the following command to change configuration interactively:

```commandline
upsolver configure
```

### Sub-Commands
To list all available sub-commands
```commandline
upsolver --help
```

Every sub-command has its own help, for example:
```commandline
upsolver execute --help
```

### Using Profiles
You can perform commands using different profiles by passing the `-p` or `--profile` flag to the `upsolver` command:

```commandline
upsolver -p profile2 login
upsolver -p profile2 configure
upsolver -p profile2 catalogs ls
```

Different profiles can have different API tokens, as well as different API endpoints, output formats, etc.


## Development

### First, Install Python
Min. required version is 3.10. Here's how to install it using `pyenv` (https://github.com/pyenv/pyenv#installation) on macos:

```commandline
brew install pyenv
pyenv install 3.10.0
pyenv global 3.10.0
```

### Install `poetry` and project dependencies

```commandline
brew install poetry
poetry install
```

You can now use `poetry`s shell or `poetry run` command:
```commandline
poetry shell
src/main.py
```

or

```commandline
poetry run src/main.py
```

### Install `pre-commit` hooks

```commandline
pre-commit install
pre-commit run --all-files
```

### Building the Project

```commandline
poetry build
```

### Generating Homebrew Formula
Since homebrew formulas are expected to list project dependencies explicitly, there's a script to generate them from the `poetry.lock` file. This script is also used by the "Create Release" workflow.

```commandline
$ scripts/gen-brew-formula.py --help                                                                                                                          130 ↵
Usage: gen-brew-formula.py [OPTIONS]

  Generates brew Formula based on poetry.lock file

Options:
  --cli-archive-url TEXT
  --compute-hash-from-build
  --compute-hash-from-file TEXT
  --poetry-lock-path TEXT
  --formula-template-path TEXT
  --formula-out-path TEXT
  --help                         Show this message and exit.
```
