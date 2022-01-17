import configparser
import csv
import io
import logging
import os
from enum import Enum
from pathlib import Path
from typing import Any, Callable, NamedTuple, Optional

import simplejson as json

from cli.errors import BadConfig, ConfigReadFail, InternalErr


class OutputFmt(Enum):
    JSON = 1
    CSV = 2
    TXT = 3


class Profile(NamedTuple):
    """
    Describes a '[profile.xxx]' section in the configuration file.

    Default profile section is written as '[profile]'.

    A section is created for you when you run the "authenticate" command.
    """
    name: str
    token: Optional[str] = None
    base_url: Optional[str] = None  # authentication request(s) will be issued to this endpoint
    output: OutputFmt = OutputFmt.JSON

    def is_default(self) -> bool:
        return self.name == 'default'


class ProfileAuthSettings(NamedTuple):
    """
    Expresses the configuration recieved from authentication endpoint
    """
    token: str
    base_url: str

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
    profiles: list[Profile]
    options: Optional[Options]
    debug: bool  # user has used the --debug flag


# class FormatterO(metaclass=ABCMeta):
#     @abstractmethod
#     def fmt_namedtuple(self, x: NamedTuple) -> str:
#         pass
#
#     def fmt_dict(self, d: dict) -> str:
#         pass
#
#
# class JsonFormatter(FormatterO):
#     def fmt(self, x: NamedTuple) -> str:
#         return json.dumps(x._asdict())
#

Formatter = Callable[[Any], str]


def fmt_json(x: Any) -> str:
    def dumps(y: Any) -> str:
        return json.dumps(y, indent=2)

    if type(x) is list:
        return '\n'.join([dumps(xx) for xx in x])
    else:
        return dumps(x)

    # dumps_args = {
    #     "obj": x._asdict() if hasattr(x, '_asdict') else x,  # NamedTuple
    #     "indent": 2
    # }
    # return json.dumps(**dumps_args)


def fmt_csv(x: Any) -> str:
    if type(x) is not list:  # TODO should work for now...
        raise InternalErr(f'Expected list of dictonaries, got: {x}')

    def to_dict(o: Any) -> dict[Any, Any]:
        if hasattr(o, '_asdict'):
            return o._asdict()
        elif type(o) is dict:
            return o
        else:
            raise InternalErr(f'{o} is not a dict')

    with io.StringIO() as o:
        w = csv.DictWriter(o, fieldnames=list(to_dict(x[0])), quoting=csv.QUOTE_NONNUMERIC)
        w.writeheader()
        for r in x:
            w.writerow(to_dict(r))
        return o.getvalue()


# class IConfMan(metaclass=ABCMeta):
#     conf: Config
#
#     @abstractmethod
#     def get_formatter(self) -> Formatter:
#         pass
#
#     @abstractmethod
#     def update_profile(self, profile: Profile) -> Config:
#         pass
#
#
# class TestConfMan(IConfMan):
#     def __init__(self):
#         default_profile = Profile(name='default')
#         self.conf = Config(
#             active_profile=default_profile,
#             profiles=[default_profile],
#             options=None,
#             debug=False
#         )
#
#     def get_formatter(self) -> Formatter:
#         return fmt_json
#
#     def update_profile(self, profile: Profile) -> Config:
#         pass
#

class ConfMan(object):
    """
    Configuration Manager. All access (read/write/modify) to Config (and underlying configuration
    file if one exists) goes through the ConfMan.
    """

    CLI_HOME_DIR: Path = Path(Path.home() / '.upsql')
    CLI_DEFAULT_LOG_PATH: Path = CLI_HOME_DIR / 'cli.log'
    CLI_DEFAULT_BASE_URL = 'localhost:8080'  # TODO api.upsolver.com or w/e

    conf_path: Path
    conf: Config

    @staticmethod
    def _get_confparser(path: Path) -> configparser.ConfigParser:
        confparser = configparser.ConfigParser()

        # create the config file if it doesn't exist
        if (not path.exists()) and path.parent.exists() and path.parent.is_dir():
            path.touch()

        try:
            if confparser.read(path) != [str(path)]:
                raise ConfigReadFail(path)
        except Exception as ex:
            raise ConfigReadFail(path, why=str(ex))
        return confparser

    @staticmethod
    def _parse_conf_file(path: Path, profile: Optional[str], debug: bool) -> Config:
        def get_log_file_path(parser: configparser.ConfigParser) -> Path:
            path_str = parser.get('options', 'log_file', fallback=None)
            if path_str is not None:
                return Path(os.path.expanduser(path_str))
            else:
                return ConfMan.CLI_DEFAULT_LOG_PATH

        def get_log_lvl(parser: configparser.ConfigParser) -> LogLvl:
            lvl_str: str = \
                'DEBUG' if debug else parser.get('options', 'log_level', fallback='')
            if lvl_str != '':
                return LogLvl[lvl_str]
            else:
                return LogLvl.CRITICAL

        confparser = ConfMan._get_confparser(path)

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
            debug=debug
        )

    def __init__(self, path: Path, profile: Optional[str] = None, debug: bool = False) -> None:
        self.conf_path = path
        self.conf = self._parse_conf_file(self.conf_path, profile, debug)

    def get_formatter(self) -> Formatter:
        desired_fmt = self.conf.active_profile.output
        if desired_fmt == OutputFmt.JSON:
            return fmt_json
        elif desired_fmt == OutputFmt.CSV:
            return fmt_csv
        else:
            raise InternalErr(f'Unsupported output format: {desired_fmt}')

    def update_profile(self, profile: Profile) -> Config:
        """
        creates/updates configuration of a specific profile.

        - writes to configuration file
        - updates in-mem snapshot of configuration
        - returns updated configuration
        """
        confparser = ConfMan._get_confparser(self.conf_path)
        profile_section_name = 'profile' if profile.is_default() else f'profile.{profile.name}'

        if not confparser.has_section(profile_section_name):
            confparser.add_section(profile_section_name)

        # TODO confparser should handle writing sections that are of NamedTuple type?
        confparser.set(section=profile_section_name, option='token', value=profile.token)
        confparser.set(section=profile_section_name, option='base_url', value=profile.base_url)
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
