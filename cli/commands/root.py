"""
https://upsolver.slite.com/app/filters/sharedWithMe/notes/2yWXSeWdc

authenticate
  --token
  --browser

clusters
  ls
  stats
  export
  stop
  run
  rm

catalogs
  ls
  export

tables
  ls
  export
  stats
  partitions

jobs
  ls
  export
  stats

execute
  --format
  --catalog
  --dry-run

shell

# TODO option/argument validators


OPTIONS:
  - defined in ~/.upsql/config (ini config file)
  - can be overwritten w/ '-o'/'--option' flags when running cli
  - can be overwritten by command options (e.g. output_format)

CONFIGURATION:
  - organization, username, rolename, password(?)
    -> but these are also found under [profile] section of the config file
  - values can be overwritten by ENVVARS
  - contains options(?)

"""
import os
from pathlib import Path
from typing import Optional

import click

import cli
from cli.commands.authenticate import authenticate
from cli.commands.catalogs import catalogs
from cli.commands.clusters import clusters
from cli.commands.context import CliContext
from cli.commands.execute import execute
from cli.commands.jobs import jobs
from cli.commands.shell import shell
from cli.commands.tables import tables
from cli.config import ConfMan


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.pass_context
@click.version_option(cli.__version__, prog_name='Upsolver CLI')
@click.option('-p', '--profile', default=None,
              help='Commands will be executed using this profile\'s auth token.')
@click.option('-c', '--config', default=None,
              help='path and name of the upsql configuration file')
@click.option('-o', '--option', default=list(), multiple=True,
              help='Set UpSQL option(s)')
@click.option('--debug', is_flag=True, default=False,
              help='Set logging level to DEBUG and log to stdout')
def root_command(
    ctx: click.Context,
    profile: Optional[str],
    config: Optional[str],
    option: list[str],
    debug: bool,
) -> None:
    """
    This is Upsolver.
    """
    # TODO currently ignored, unsure when or if we support these
    # clioptions = dict()
    # for o in option:
    #     section_parts = o.split('=')
    #     if len(section_parts) < 2:
    #         raise BadArgument(f'Options should be key-value pairs, e.g. X=Y')
    #     clioptions[section_parts[0]] = ''.join(section_parts[1:])

    conf_path = (
        Path(ConfMan.CLI_HOME_DIR / 'config') if config is None
        else Path(os.path.expanduser(config))
    )

    ctx.obj = CliContext(confman=ConfMan(conf_path, profile, debug))


# TODO automate this by searching commands package?
root_command.add_command(authenticate)
root_command.add_command(execute)
root_command.add_command(shell)
root_command.add_command(clusters)
root_command.add_command(catalogs)
root_command.add_command(tables)
root_command.add_command(jobs)
