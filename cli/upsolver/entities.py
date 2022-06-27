from abc import ABC
from dataclasses import dataclass
from typing import Any

from dataclasses_json import dataclass_json


class ApiEntity(ABC):
    """
    Represents objects that are return from the API.

    Unlike "raw entities", ApiEntities are more suitable for the semantics used in CLI code.
    (e.g. EnvironmentDashboardResponse is mapped to Cluster, and often the ApiEntities will be
     more simple, i.e. contain only the relevant data for the CLI).
    """
    pass


@dataclass_json
@dataclass
class Catalog(ApiEntity):
    id: str
    name: str
    created_by: str
    kind: str
    org_id: str


@dataclass_json
@dataclass
class Cluster(ApiEntity):
    name: str
    id: str
    running: bool


@dataclass_json
@dataclass
class Table(ApiEntity):
    id: str
    name: str
    compression: str
    is_running: bool


@dataclass_json
@dataclass
class TablePartition(ApiEntity):
    table_name: str
    name: str


@dataclass_json
@dataclass
class Job(ApiEntity):
    id: str
    name: str
    status: str


ExecutionResult = list[dict[Any, Any]]
ExecutionErr = Exception
NextResultPath = str  # results are paged, with "next pointer" being a path of url
