import configparser
import logging
import os
from enum import Enum
from pathlib import Path
from typing import NamedTuple, Optional

from yarl import URL

from cli.errors import ConfigErr, ConfigReadFail, InternalErr
from cli.formatters import Formatter, OutputFmt
from cli.utils import ensure_exists, parse_url


class Profile(NamedTuple):
    """
    Describes a '[profile.xxx]' section in the configuration file.

    Default profile section is written as '[profile]'.

    A section is created for you when you run the "authenticate" command.
    """
    name: str
    token: Optional[str] = None
    base_url: Optional[URL] = None
    output: Optional[OutputFmt] = None

    def is_default(self) -> bool:
        return self.name == 'default'


class ProfileAuthSettings(NamedTuple):
    """
    Expresses the configuration recieved from authentication endpoint

    base_url is used to retrieve another base url that will be used for futher requests (it may
    or may not be different)
    """
    token: str
    base_url: URL

    def update(self, p: Profile) -> Profile:
        """
        Return copy of profile p, updated with auth settings
        """
        return p._replace(token=self.token, base_url=self.base_url)


def get_auth_settings(profile: Profile) -> Optional[ProfileAuthSettings]:
    return ProfileAuthSettings(
        token=profile.token,
        base_url=profile.base_url
    ) if (profile.token is not None) and (profile.base_url is not None) else None


class LogLvl(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

    def to_logging(self) -> int:
        if self.value == LogLvl.DEBUG.value:
            return logging.DEBUG
        elif self.value == LogLvl.INFO.value:
            return logging.INFO
        elif self.value == LogLvl.WARNING.value:
            return logging.WARNING
        elif self.value == LogLvl.ERROR.value:
            return logging.ERROR
        elif self.value == LogLvl.CRITICAL.value:
            return logging.CRITICAL
        raise InternalErr(f'cannot convert LogLvl={self.value} to logging (package) level')


class Options(NamedTuple):
    log_file: Path
    log_level: LogLvl


class Config(NamedTuple):
    active_profile: Profile
    profiles: list
    options: Optional[Options]
    verbose: bool  # user has used the --verbose flag


def get_home_dir() -> Path:
    from_env = os.environ.get('UPSOLVER_HOME')
    return Path(from_env) if from_env is not None \
        else Path(Path.home() / '.upsolver')


class ConfigurationManager(object):
    """
    Configuration Manager. All access (read/write/modify) to Config (and underlying configuration
    file if one exists) goes through the ConfMan.
    """

    CLI_HOME_DIR: Path = get_home_dir()
    CLI_DEFAULT_LOG_PATH: Path = CLI_HOME_DIR / 'cli.log'
    CLI_DEFAULT_BASE_URL = parse_url('https://api.upsolver.com/')
    DEFAULT_OUTPUT_FMT = OutputFmt.JSON

    conf_path: Path
    conf: Config
    auth_api_url: URL

    @staticmethod
    def _get_confparser(path: Path) -> configparser.ConfigParser:
        ensure_exists(path)
        confparser = configparser.ConfigParser()
        try:
            if confparser.read(path) != [str(path)]:
                raise ConfigReadFail(path)
        except Exception as ex:
            raise ConfigReadFail(path, why=str(ex))
        return confparser

    @staticmethod
    def _parse_conf_file(path: Path, profile: Optional[str], verbose: bool) -> Config:
        def get_log_file_path(parser: configparser.ConfigParser) -> Path:
            path_str = parser.get('options', 'log_file', fallback=None)
            if path_str is not None:
                return Path(os.path.expanduser(path_str))
            else:
                return ConfigurationManager.CLI_DEFAULT_LOG_PATH

        def get_log_lvl(parser: configparser.ConfigParser) -> LogLvl:
            lvl_str: str = \
                'DEBUG' if verbose else parser.get('options', 'log_level', fallback='')
            if lvl_str != '':
                return LogLvl[lvl_str]
            else:
                return LogLvl.CRITICAL

        confparser = ConfigurationManager._get_confparser(path)

        profiles: list = list()
        for profile_section in [section for section in confparser.sections()
                                if section.startswith("profile")]:
            section_parts = profile_section.split('.')
            if len(section_parts) != 2 and profile_section != "profile":
                raise ConfigErr(f'invalid profile section name: "{profile_section}". '
                                f'profile section should of the form: [profile.name] '
                                f'(or [profile] for default profile)')

            conf_fmt = confparser.get(profile_section, 'output', fallback=None)
            try:
                output_fmt = OutputFmt(conf_fmt.lower()) if conf_fmt else None
            except ValueError:
                raise ConfigErr(f'Invalid output format defined in "{profile_section}": {conf_fmt}')

            profiles.append(
                Profile(
                    name=section_parts[1] if len(section_parts) > 1 else "default",
                    token=confparser.get(profile_section, 'token', fallback=None),
                    base_url=parse_url(confparser.get(profile_section, 'base_url', fallback=None)),
                    output=output_fmt
                )
            )

        desired_profile_name = profile if profile is not None else 'default'
        active_profile = next(
            (p for p in profiles if p.name == desired_profile_name),
            Profile(name=desired_profile_name)
        )

        return Config(
            active_profile=active_profile,
            profiles=profiles,
            options=Options(
                log_file=get_log_file_path(confparser),
                log_level=get_log_lvl(confparser)
            ),
            verbose=verbose
        )

    def __init__(self, path: Path,
                 profile: Optional[str] = None,
                 verbose: bool = False,
                 auth_api_url: Optional[URL] = None) -> None:
        self.conf_path = path
        self.auth_api_url = auth_api_url or self.CLI_DEFAULT_BASE_URL
        assert self.auth_api_url.is_absolute()
        self.conf = self._parse_conf_file(self.conf_path, profile, verbose)

    def get_formatter(self) -> Formatter:
        fmt = self.conf.active_profile.output or self.DEFAULT_OUTPUT_FMT
        return fmt.get_formatter()

    def update_profile(self, profile: Profile, force: bool = False) -> Config:
        """
        creates/updates configuration of a specific profile.

        - writes to configuration file
        - updates in-mem snapshot of configuration
        - returns updated configuration
        """
        confparser = ConfigurationManager._get_confparser(self.conf_path)
        profile_section_name = 'profile' if profile.is_default() else f'profile.{profile.name}'

        if confparser.has_section(profile_section_name):
            if not force:
                raise ConfigErr(f"Profile '{profile_section_name}' already exists. In order to overwite it"
                                f" please use the '--force' flag.")
            confparser.remove_section(profile_section_name)

        confparser.add_section(profile_section_name)

        # TODO confparser should handle writing sections that are of NamedTuple type?
        if profile.token:
            confparser.set(section=profile_section_name, option='token', value=profile.token)
        if profile.base_url:
            confparser.set(section=profile_section_name, option='base_url', value=str(profile.base_url))
        if profile.output:
            confparser.set(section=profile_section_name, option='output', value=profile.output.name)

        with open(self.conf_path, 'w') as conf_file:
            confparser.write(conf_file)

        self.conf = self.conf._replace(
            active_profile=(
                profile if self.conf.active_profile.name == profile.name
                else self.conf.active_profile
            ),
            profiles=[p for p in self.conf.profiles if p.name != profile.name] + [profile]
        )

        return self.conf
