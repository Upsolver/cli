#!/usr/bin/env python

"""
CTRL+D

# type hints cheat sheet: https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html

- config location
  default: ~/.upsql/
"""
from cli.commands.root import root_command

if __name__ == '__main__':
    root_command()
