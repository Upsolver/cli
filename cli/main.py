#!/usr/bin/env python

"""
CTRL+D

# type hints cheat sheet: https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html

- config location
  default: ~/.upsolver/
"""
from click import echo
from requests.exceptions import ConnectionError
from yarl import URL

from cli.commands.root import root_command
from cli.errors import ApiErr


def main() -> None:
    try:
        root_command()
    except ConnectionError as ex:
        url = URL(ex.request.url)
        echo(err=True, message=f'Connection to \'{url.host}:{url.port}\' failed...')
    except NotImplementedError:
        echo(err=True, message='This command is not yet implemented')
    except ApiErr as ex:
        echo(err=True, message=f'Upsolver API error: {ex}')


if __name__ == '__main__':
    main()
