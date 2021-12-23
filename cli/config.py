import logging
from enum import Enum
from pathlib import Path
from typing import NamedTuple, Optional

from cli.errors import InternalErr

CLI_HOME_DIR = Path(Path.home() / '.upsql')


class OutputFmt(Enum):
    JSON = 1
    CSV = 2


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


class LogLvl(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

    def to_logging(self) -> int:
        if self.value == LogLvl.DEBUG:
            return logging.DEBUG
        elif self.value == LogLvl.INFO:
            return logging.INFO
        elif self.value == LogLvl.WARNING:
            return logging.WARNING
        elif self.value == LogLvl.ERROR:
            return logging.ERROR
        elif self.value == LogLvl.CRITICAL:
            return logging.CRITICAL
        raise InternalErr(f'cannot convert LogLvl={self.value} to logging (package) level')


class Options(NamedTuple):
    log_file: Path
    log_level: LogLvl


class Config(NamedTuple):
    active_profile: Profile
    profiles: list[Profile]
    options: Options
