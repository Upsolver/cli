import configparser
import logging
from logging.handlers import RotatingFileHandler
from typing import Callable

import coloredlogs

from cli.config import Config, LogLvl, Profile, ProfileAuthSettings
from cli.errors import InternalErr
from cli.upsolver import UpsolverApi


class CliContext(object):
    conf: Config
    log: logging.Logger

    """
    This is used as the value for click.Context object that is passed to subcommands.

    CliContext holds "global" information (e.g. configuration) and is capable of spawning
    entities that depend on this configuration (e.g. loggers).
    """
    def _setup_logging(self, conf: Config) -> None:
        self.log = logging.getLogger('CLI')

        lvl = (LogLvl.DEBUG if conf.debug else conf.options.log_level).to_logging()
        coloredlogs.install(level=lvl)

        formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')

        # always write to file
        handlers: list[logging.Handler] = [RotatingFileHandler(
            filename=conf.options.log_file,
            maxBytes=10 * (2 ** 20),
        )]
        # if debug mode, also write to stderr
        if conf.debug:
            handlers.append(logging.StreamHandler())

        for h in handlers:
            h.setLevel(lvl)
            h.setFormatter(formatter)
            self.log.addHandler(h)

    def __init__(self, conf: Config):
        self.conf = conf
        self._setup_logging(conf)

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

    def authenticator(self) -> Callable[[str], ProfileAuthSettings]:
        """
        Authenticator is separate from UpsolverApi because authentication calls are made
        to a (potentially?) different endpoints - so stricly speaking, auth endpoint isn't
        part of the (user) upsolver API
        :return:
        """
        def dummy_auth(token: str) -> ProfileAuthSettings:
            self.log.debug(f'authenticating token: {token} ...')
            return ProfileAuthSettings(token=token, base_url='stam://upsolver.com')

        return dummy_auth
