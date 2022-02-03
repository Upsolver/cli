import csv
import io
from typing import Any, Callable

import simplejson as json

from cli.errors import InternalErr

Formatter = Callable[[Any], str]


def fmt_json(x: Any) -> str:
    def dumps(y: Any) -> str:
        return json.dumps(y, indent=2)

    if type(x) is list:
        return '\n'.join([dumps(xx) for xx in x])
    else:
        return dumps(x)


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
