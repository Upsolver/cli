from pathlib import Path
from typing import Optional


class InternalErr(Exception):
    pass


class BadArgument(ValueError):
    pass


class ConfigErr(Exception):
    pass


class ConfigReadFail(ConfigErr):
    def __init__(self, path: Path, why: Optional[str] = None):
        super(ConfigReadFail, self).__init__(
            f'Failed to read configuration from {path}' + ('' if why is None else f': {why}')
        )


class ApiErr(Exception):
    pass
