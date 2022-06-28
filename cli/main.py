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
from cli.commands.catalogs import catalogs
from cli.commands.clusters import clusters
from cli.commands.configure import configure
from cli.commands.context import CliContext
from cli.commands.execute import execute
from cli.commands.jobs import jobs
from cli.commands.login import login
from cli.commands.tables import tables
from cli.config import ConfigurationManager


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.pass_context
@click.version_option(clipkg.__version__, prog_name='Upsolver CLI')
@click.option('-p', '--profile', default=None,
              help='Commands will be executed using this profile\'s auth token.')
@click.option('-c', '--config', default=None,
              help='path and name of the upsql configuration file.')
@click.option('--debug', is_flag=True, default=False,
              help='Set logging level to DEBUG and log to stdout.')
def cli(
    ctx: click.Context,
    profile: Optional[str],
    config: Optional[str],
    debug: bool,
) -> None:
    """
    Upsolver CLI
    """

    conf_path = (
        Path(ConfigurationManager.CLI_HOME_DIR / 'config') if config is None
        else Path(os.path.expanduser(config))
    )

    ctx.obj = CliContext(confman=ConfigurationManager(conf_path, profile, debug))


cli.add_command(login)
cli.add_command(configure)
cli.add_command(execute)
cli.add_command(clusters)
cli.add_command(catalogs)
cli.add_command(tables)
cli.add_command(jobs)


def exit_with(code: errors.ExitCode, msg: str) -> None:
    if '--debug' in sys.argv:
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
