from pathlib import Path
from typing import Any


def ensure_exists(path: Path) -> None:
    if not path.exists():
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        path.touch()


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
