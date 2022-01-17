# cli
The Upsolver Command Line Interface.

## Getting Started

- Install Python (https://github.com/pyenv/pyenv#installation, min required version: 3.10):
```commandline
brew install pyenv
pyenv install 3.10.0
pyenv global 3.10.0
```

- Install poetry (https://python-poetry.org/docs/#installation), and active its shell:

```commandline
brew install poetry
```

run these commands from `cli` repo root:

```commandline
poetry install
poetry shell
```

- Run the CLI:

```commandline
cli/main.py
```

## Development

```commandline
pre-commit install
pre-commit run --all-files
```

```commandline
poetry build
```
