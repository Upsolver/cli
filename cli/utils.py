import logging
from logging import Logger
from pathlib import Path
from typing import Any, Dict, Optional, Protocol, Type, TypeVar

import click
from yarl import URL

from cli import errors

seconds_per_unit = {'s': 1.0, 'm': 60.0}


def convert_to_seconds(s: str) -> float:
    return float(s[:-1]) * seconds_per_unit[s[-1]]


def convert_time_str(ctx: click.Context, param, value: Any) -> Any:
    try:
        return convert_to_seconds(value)
    except Exception:
        raise errors.InvalidOptionErr(f'Cannot convert \'{value}\' to seconds '
                                      '(valid examples: 0.25s, 1.5m)')


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

    # We remove the path since we rely on it being empty when we append other paths in the program
    burl = URL(url).with_path("")
    if burl.is_absolute():
        return burl
    else:
        if url.startswith('localhost'):
            return URL('http://' + url)
        else:
            return URL('https://' + url)


def flatten(d: dict, parent: Optional[str] = None, sep: str = '.') -> dict:
    """
    flatten({'a': {'b': {'c': 1}}, 'd': {'e': [1, 2, 3]}, 'f': 'foo'})
    returns
    {'a.b.c': 1, 'd.e': [1, 2, 3], 'f': 'foo'}

    :param d: dictionary to flatten
    :param parent: name of parent key; used for recursion
    :param sep: separator between concatenated key names
    :return: flattened dictionary
    """
    items: list = []
    for k, v in d.items():
        new_key = f'{parent}{sep}{k}' if parent is not None else k
        if type(v) is dict:
            items.extend(flatten(v, parent=new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class NestedDictAccessor(object):
    def __init__(self, d: dict) -> None:
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
    __dataclass_fields__: Dict


TAnyDataclass = TypeVar('TAnyDataclass', bound=AnyDataclass)


def from_dict(tpe: Type[TAnyDataclass], d: dict) -> TAnyDataclass:
    return tpe.from_dict(d)


class HasId(Protocol):
    id: str


class HasNameAndId(Protocol):
    id: str
    name: str


THasNameAndId = TypeVar('THasNameAndId', bound='HasNameAndId')


def find_by_name_or_id(name_or_id: str, ls: list) -> THasNameAndId:
    for x in ls:
        if x.name == name_or_id or x.id == name_or_id:
            return x

    raise errors.EntityNotFound(name_or_id, [f'(id={x.id}, name={x.name}]' for x in ls])


THasId = TypeVar('THasId', bound='HasId')


def find_by_id(id: str, ls: list) -> THasId:
    for x in ls:
        if x.id == id:
            return x

    raise errors.EntityNotFound(id, [x.id for x in ls])
