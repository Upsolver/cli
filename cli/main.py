#!/usr/bin/env python

from click import echo
from requests.exceptions import ConnectionError
from yarl import URL

from cli.commands.root import root_command
from cli.errors import ApiErr, ConfigErr


def main() -> None:
    try:
        root_command()
    except ConnectionError as ex:
        url = URL(ex.request.url)
        echo(err=True, message=f'Connection to \'{url.host}:{url.port}\' failed...')
    except NotImplementedError:
        echo(err=True, message='This command is not yet implemented')
    except ApiErr as ex:
        echo(err=True, message=f'{ex}')
    except ConfigErr as ex:
        echo(err=True, message=f'Configuration error: {ex}')


if __name__ == '__main__':
    main()
