from dataclasses import dataclass
from typing import Any

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Catalog:
    id: str
    name: str
    created_by: str
    kind: str
    org_id: str


@dataclass_json
@dataclass
class Cluster:
    name: str
    id: str
    running: bool


@dataclass_json
@dataclass
class Table:
    id: str
    name: str
    compression: str
    is_running: bool


@dataclass_json
@dataclass
class TablePartition:
    table_name: str
    name: str


@dataclass_json
@dataclass
class Job:
    id: str
    name: str
    status: str


ExecutionResult = list[dict[Any, Any]]
ExecutionErr = Exception
NextResultPath = str  # results are paged, with "next pointer" being a path of url
