import os
from pathlib import Path
from typing import Optional

import click

import cli
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
@click.version_option(cli.__version__, prog_name='Upsolver CLI')
@click.option('-p', '--profile', default=None,
              help='Commands will be executed using this profile\'s auth token.')
@click.option('-c', '--config', default=None,
              help='path and name of the upsql configuration file')
@click.option('--debug', is_flag=True, default=False,
              help='Set logging level to DEBUG and log to stdout')
def root_command(
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


root_command.add_command(login)
root_command.add_command(configure)
root_command.add_command(execute)
# root_command.add_command(shell)
root_command.add_command(clusters)
root_command.add_command(catalogs)
root_command.add_command(tables)
root_command.add_command(jobs)
