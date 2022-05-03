import logging
from logging import Logger
from pathlib import Path
from typing import Any, Dict, Optional, Protocol

from yarl import URL


def get_logger(path: Optional[str] = None) -> Logger:
    """
    Use this method to get logger instances. It uses the "CLI" logger as the "root" logger, thus
    all logger instances returned from this function will share the root logger's configuration.

    :param path: a dot-separated path, e.g. "Requester", or "Something.Other"
    :return:
    """
    if path is not None:
        return logging.getLogger(f'CLI.{path}')
    else:
        return logging.getLogger('CLI')


def ensure_exists(path: Path) -> None:
    """
    Ensures file exists for the provided path.
    """
    if not path.exists():
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        path.touch()


def parse_url(url: Optional[str]) -> Optional[URL]:
    if url is None:
        return None

    burl = URL(url)
    if burl.is_absolute():
        return burl
    else:
        if url.startswith('localhost'):
            return URL('http://' + url)
        else:
            return URL('https://' + url)


class NestedDictAccessor(object):
    def __init__(self, d: dict[Any, Any]) -> None:
        self.d = d

    def __getitem__(self, item: Any) -> Any:
        def throw() -> None:
            raise KeyError(f'Missing {item} in {self.d}')

        curr: Any = self.d  # type annotation is a hack...
        for path_part in item.split('.'):
            if type(curr) is not dict:
                throw()
            v = curr.get(path_part)
            if v is None:
                throw()
            curr = v
        return curr


# Protocol == structural typing support (https://peps.python.org/pep-0544/)
class AnyDataclass(Protocol):
    __dataclass_fields__: Dict[Any, Any]
