import csv
import io
from typing import Any, Callable

import simplejson as json
from tabulate import tabulate

from cli.errors import InternalErr

Formatter = Callable[[Any], str]


def to_dict(o: Any) -> dict[Any, Any]:
    if hasattr(o, '_asdict'):
        return o._asdict()
    elif type(o) is dict:
        return o
    else:
        raise InternalErr(f'{o} is not a dict')


def fmt_json(x: Any) -> str:
    def dumps(y: Any) -> str:
        return json.dumps(y, indent=2)

    if type(x) is list:
        return '\n'.join([dumps(xx) for xx in x])
    else:
        return dumps(x)


def fmt_csv(delimiter: str = ',') -> Callable[[Any], str]:
    def fmt(x: Any) -> str:
        if type(x) is not list:  # TODO should work for now...
            raise InternalErr(f'Expected list of dictonaries, got: {x}')

        with io.StringIO() as o:
            w = csv.DictWriter(
                o,
                delimiter=delimiter,
                fieldnames=list(to_dict(x[0])),
                quoting=csv.QUOTE_NONNUMERIC
            )

            w.writeheader()
            for r in x:
                w.writerow(to_dict(r))
            return o.getvalue()

    return fmt


def fmt_plain(x: Any) -> str:
    if type(x) is not list:  # TODO should work for now...
        raise InternalErr(f'Expected list of dictonaries, got: {x}')

    if len(x) == 0:
        return ''

    return tabulate(
        [to_dict(r).values() for r in x],
        headers=list(to_dict(x[0]))
    )
