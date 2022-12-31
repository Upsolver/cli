import csv
import dataclasses
import io
import json
from enum import Enum
from functools import partial
from json import JSONEncoder
from typing import Any, Callable, Optional, Protocol

from tabulate import tabulate

from cli import errors
from cli.utils import flatten


class Formatter(Protocol):
    def do_fmt(self, value: Any) -> str:
        raise NotImplementedError("Missing implemenation of fmt")


class OutputFmt(Enum):
    JSON = 'json'
    CSV = 'csv'
    TSV = 'tsv'
    PLAIN = 'plain'

    def get_formatter(self) -> Formatter:
        if self == OutputFmt.JSON:
            return JsonFormatter()
        elif self == OutputFmt.CSV:
            return CsvFormatter()
        elif self == OutputFmt.TSV:
            return CsvFormatter().withDelimiter('\t')
        elif self == OutputFmt.PLAIN:
            return PlainFormatter()
        else:
            raise errors.InternalErr(f'Unsupported output format: {self}')


def to_dict_maybe(o: Any) -> Optional[dict]:
    if type(o) is dict:
        return o
    elif dataclasses.is_dataclass(o):
        return dataclasses.asdict(o)
    elif hasattr(o, '_asdict'):
        return o
    else:
        return None


class JsonFormatter():
    def do_fmt(self, value: Any) -> str:
        class DataclassesJSONEncoder(JSONEncoder):
            def default(self, o: Any) -> dict:
                if dataclasses.is_dataclass(o):
                    return dataclasses.asdict(o)
                return super().default(o)

        def dumps(y: Any) -> str:
            return json.dumps(y, cls=DataclassesJSONEncoder, indent=2)

        if type(value) is list:
            return '\n'.join([dumps(xx) for xx in value])
        elif type(value) is str:
            return value
        else:
            return dumps(value)


def fmt_any(x: Any, fmt_list: Callable[[list], str]) -> str:
    if type(x) is list:
        return fmt_list(x)
    elif type(x) is str:
        return x
    else:
        return fmt_list([x])


def to_dict_or_raise(x: Any, desired_fmt: OutputFmt) -> dict:
    maybe_dict = to_dict_maybe(x)
    if maybe_dict is None:
        raise errors.FormattingErr(v=x, desired_fmt=desired_fmt.name)
    return maybe_dict


class CsvFormatter():

    delimiter = ','

    def withDelimiter(self, delimiter: chr):
        self.delimiter = delimiter
        return self

    def fmt_list(self, xs: list) -> str:
        if len(xs) == 0:
            return ''

        to_dict: Callable[[Any], dict] = partial(to_dict_or_raise, desired_fmt=OutputFmt.CSV)

        dicts = [flatten(to_dict(x)) for x in xs]
        keys = sorted(set().union(*dicts))

        with io.StringIO() as o:
            w = csv.DictWriter(
                o,
                delimiter=self.delimiter,
                fieldnames=keys,
                quoting=csv.QUOTE_NONNUMERIC,
                restval="<null>"
            )

            w.writeheader()
            for x in dicts:
                w.writerow(x)
            return o.getvalue()

    def do_fmt(self, value: Any) -> str:
        return fmt_any(value, fmt_list=self.fmt_list)


class PlainFormatter():

    def fmt_list(self, xs: list) -> str:
        to_dict: Callable[[Any], dict] = \
            partial(to_dict_or_raise, desired_fmt=OutputFmt.PLAIN)
        if len(xs) == 0:
            return ''

        return tabulate(
            [to_dict(x).values() for x in xs],
            headers=list(to_dict(xs[0]))
        )

    def do_fmt(self, value: Any) -> str:
        return fmt_any(value, fmt_list=self.fmt_list)


def get_output_format(output_format: Optional[str]) -> OutputFmt:
    if output_format is not None:
        try:
            return OutputFmt(output_format.lower())
        except ValueError:
            raise errors.ConfigErr("Output format {} is not supported. "
                                   "Supported formats: Json, Csv, Tsv, Plain.".format(output_format))
