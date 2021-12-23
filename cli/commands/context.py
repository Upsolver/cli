import configparser
import logging

import coloredlogs

from cli.config import Config, Profile
from cli.errors import InternalErr
from cli.upsolver import UpsolverApi


class CliContext(object):
    conf: Config

    """
    This is used as the value for click.Context object that is passed to subcommands.

    CliContext holds "global" information (e.g. configuration) and is capable of spawning
    entities that depend on this configuration (e.g. loggers).
    """
    @staticmethod
    def _setup_logging(conf: Config) -> None:
        lvl = conf.options.log_level.to_logging()
        coloredlogs.install(level=lvl)

        # always write to file
        handlers: list[logging.Handler] = [logging.FileHandler(conf.options.log_file)]
        # if debug mode, also write to stderr
        if conf.debug:
            handlers.append(logging.StreamHandler())

        logging.basicConfig(
            level=lvl,
            handlers=handlers
        )

    def __init__(self, conf: Config):
        self.conf = conf
        self._setup_logging(conf)

    def logger(self, name: str) -> logging.Logger:
        # TODO if conf has a file configured, use that to write to file
        #  also: if debug flag is set, output to stdout
        return logging.getLogger(name)

    def update_profile_conf(self, new_profile: Profile) -> None:
        confparser = configparser.ConfigParser()

        # TODO refactor, look at get_config() in root.py
        if confparser.read(self.conf.conf_path) != [str(self.conf.conf_path)]:
            raise InternalErr(f'Failed to read configuration file from {self.conf.conf_path}')

        profile_section_name = \
            'profile' if new_profile.is_default() else f'profile.{new_profile.name}'

        if not confparser.has_section(profile_section_name):
            confparser.add_section(profile_section_name)

        # TODO confparser should handle writing sections that are of NamedTuple type
        confparser.set(section=profile_section_name, option='token', value=new_profile.token)
        confparser.set(section=profile_section_name, option='base_url', value=new_profile.base_url)
        confparser.set(section=profile_section_name, option='output',
                       value=new_profile.output.name)

        with open(self.conf.conf_path, 'w') as conf_file:
            confparser.write(conf_file)

    def upsolver_api(self) -> UpsolverApi:
        # TODO this is used from both the interactive shell and the execute subcommand...
        #      will also have to build the api for tests, and for local development
        # TODO what configuration is needed
        #      - from ~/.upsql/config?
        #      - env vars (overrides)
        #      - explicit values passed from cli invocation
        return UpsolverApi()
