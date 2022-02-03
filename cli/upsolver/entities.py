from typing import NamedTuple, Optional


class Cluster(NamedTuple):
    name: str
    id: str
    running: bool


class Catalog(NamedTuple):
    id: str
    name: str
    created_by: Optional[str]
    kind: str
    orgId: str


class Table(NamedTuple):
    id: str
    name: str


class TablePartition(NamedTuple):
    table_name: str
    name: str


class Job(NamedTuple):
    name: str
    status: str
