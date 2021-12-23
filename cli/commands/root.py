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
import configparser
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
from cli.commands.shell import shell
from cli.config import CLI_HOME_DIR, Config, LogLvl, Options, OutputFmt, Profile
from cli.errors import BadArgument, BadConfig, InternalErr


@click.group()
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
    def get_config_path() -> Path:
        if config is not None:
            # we call expanduser to make usage of '~' possible
            pconf = Path(os.path.expanduser(config))
            if not pconf.exists():
                raise BadArgument(f'Invalid config path: {config} does not exist')
            return pconf
        else:
            return CLI_HOME_DIR / 'config'

    def get_log_file_path(parser: configparser.ConfigParser) -> Path:
        path_str = parser.get('options', 'log_file', fallback=None)
        if path_str is not None:
            return Path(os.path.expanduser(path_str))
        else:
            return CLI_HOME_DIR / 'cli.log'

    def get_log_lvl(parser: configparser.ConfigParser) -> LogLvl:
        lvl_str: str = \
            'DEBUG' if debug else parser.get('options', 'log_level', fallback='')
        if lvl_str != '':
            return LogLvl[lvl_str]
        else:
            return LogLvl.CRITICAL

    def get_config() -> Config:
        confparser = configparser.ConfigParser()
        config_path = get_config_path()
        if confparser.read(config_path) != [str(config_path)]:
            raise InternalErr(f'Failed to read configuration file from {config_path}')

        profiles: list[Profile] = list()
        for profile_section in [section for section in confparser.sections()
                                if section.startswith("profile")]:
            section_parts = profile_section.split('.')
            if len(section_parts) != 2 and profile_section != "profile":
                raise BadConfig(f'invalid profile section name: "{profile_section}". '
                                f'profile section should of the form: [profile.name] '
                                f'(or [profile] for default profile)')

            profiles.append(
                # TODO handle KeyError exception of OutputFmt
                Profile(
                    name=section_parts[1] if len(section_parts) > 1 else "default",
                    token=confparser.get(profile_section, 'token', fallback=None),
                    base_url=confparser.get(profile_section, 'base_url', fallback=None),
                    output=OutputFmt[confparser.get(profile_section, 'output', fallback='JSON')]
                )
            )

        # TODO currently ignored, unsure when or if we support these
        # clioptions = dict()
        # for o in option:
        #     section_parts = o.split('=')
        #     if len(section_parts) < 2:
        #         raise BadArgument(f'Options should be key-value pairs, e.g. X=Y')
        #     clioptions[section_parts[0]] = ''.join(section_parts[1:])

        desired_profile_name = profile if profile is not None else 'default'
        active_profile = next(
            (p for p in profiles if p.name == desired_profile_name),
            Profile(name=desired_profile_name)
        )

        return Config(
            conf_path=get_config_path(),
            active_profile=active_profile,
            profiles=profiles,
            options=Options(
                log_file=get_log_file_path(confparser),
                log_level=get_log_lvl(confparser)
            ),
            debug=debug
        )

    ctx.obj = CliContext(
        conf=get_config(),
    )


# TODO automate this by searching commands package?
root_command.add_command(authenticate)
root_command.add_command(execute)
root_command.add_command(shell)
root_command.add_command(clusters)
root_command.add_command(catalogs)
