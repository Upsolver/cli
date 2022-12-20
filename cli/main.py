#!/usr/bin/env python
import os
import sys
import traceback
from pathlib import Path
from typing import Optional

import click
from click import echo
from requests.exceptions import ConnectionError
from yarl import URL

import cli as clipkg
from cli import errors
from cli.commands.configure import configure
from cli.commands.context import CliContext
from cli.commands.execute import execute
from cli.config import ConfigurationManager
from cli.utils import parse_url


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.pass_context
@click.version_option(clipkg.__version__, prog_name='Upsolver CLI')
@click.option('-p', '--profile', default=None,
              help='Commands will be executed using this profile\'s auth token. '
                   'The default profile is named profile.')
@click.option('-c', '--config', default=None,
              help='Path of the upsolver configuration file. Default is `~/.upsolver/config`.')
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='Set verbose output.')
def cli(
        ctx: click.Context,
        profile: Optional[str],
        config: Optional[str],
        verbose: bool) -> None:
    """
    Upsolver CLI
    """

    conf_path = (
        Path(ConfigurationManager.CLI_HOME_DIR / 'config') if config is None
        else Path(os.path.expanduser(config))
    )

    auth_api_url_env_var = os.environ.get('AUTH_API_URL')
    auth_api_url = parse_url(auth_api_url_env_var) if auth_api_url_env_var else None

    ctx.obj = CliContext(confman=ConfigurationManager(conf_path, profile, verbose, auth_api_url))


cli.add_command(configure)
cli.add_command(execute)


def exit_with(code: errors.ExitCode, msg: str) -> None:
    if '--verbose' in sys.argv:
        traceback.print_exc()

    echo(err=True, message=msg)
    sys.exit(code.value)


def main() -> None:
    try:
        cli()
    except ConnectionError as ex:
        url = URL(ex.request.url)
        exit_with(errors.ExitCode.NetworkErr, f'Connection to \'{url.host}:{url.port}\' failed...')
    except NotImplementedError:
        exit_with(errors.ExitCode.InternalErr, 'This command is not yet implemented')
    except errors.CliErr as ex:
        exit_with(ex.exit_code(), str(ex))


if __name__ == '__main__':
    main()
