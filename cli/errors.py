from pathlib import Path
from typing import Optional


class InternalErr(Exception):
    pass


# TODO(CR) use built-in if they exist
class BadArgument(Exception):
    pass


class BadConfig(Exception):
    pass


class ConfigReadFail(BadConfig):
    def __init__(self, path: Path, why: Optional[str] = None):
        super(ConfigReadFail, self).__init__(
            f'Failed to read configuration from {path}' + ('' if why is None else f': {why}')
        )


class ApiErr(Exception):
    pass
