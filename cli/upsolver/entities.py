from dataclasses import dataclass
from typing import Any


@dataclass
class Catalog:
    id: str
    name: str
    created_by: str
    kind: str
    org_id: str


@dataclass
class Cluster:
    name: str
    id: str
    running: bool


@dataclass
class Table:
    id: str
    name: str


@dataclass
class TablePartition:
    table_name: str
    name: str


@dataclass
class Job:
    name: str
    status: str


ExecutionResult = list[dict[Any, Any]]
ExecutionErr = Exception
NextResultPath = str  # results are paged, with "next pointer" being a path of url
