#!/usr/bin/env python
import sys

from click import echo
from requests.exceptions import ConnectionError
from yarl import URL

from cli import errors
from cli.commands.root import root_command


def exit_with(code: errors.ExitCode, msg: str) -> None:
    echo(err=True, message=msg)
    sys.exit(code.value)


def main():
    try:
        root_command()
    except ConnectionError as ex:
        url = URL(ex.request.url)
        exit_with(errors.ExitCode.NetworkErr, f'Connection to \'{url.host}:{url.port}\' failed...')
    except NotImplementedError:
        exit_with(errors.ExitCode.InternalErr, 'This command is not yet implemented')
    except errors.CliErr as ex:
        exit_with(ex.exit_code(), str(ex))


if __name__ == '__main__':
    main()
