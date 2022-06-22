from abc import ABC, abstractmethod
from typing import Any

from cli import errors
from cli.upsolver.entities import Table, TablePartition
from cli.upsolver.requester import Requester
from cli.utils import find_by_id

TableId = str


class RawTablesApi(ABC):
    @abstractmethod
    def get(self) -> list[dict[Any, Any]]:
        pass


class RawTablesApiProvider(ABC):
    @property
    @abstractmethod
    def raw(self) -> RawTablesApi:
        pass


class TablesApi(RawTablesApiProvider):
    @abstractmethod
    def get(self) -> list[Table]:
        pass

    @abstractmethod
    def export(self, table_id: TableId) -> str:
        pass

    @abstractmethod
    def get_partitions(self, table_id: TableId) -> list[TablePartition]:
        pass


class TablesApiProvider(ABC):
    @property
    @abstractmethod
    def tables(self) -> TablesApi:
        pass


class RawRestTablesApi(RawTablesApi):
    def __init__(self, requester: Requester):
        self.requester = requester

    def get(self) -> list[dict[Any, Any]]:
        return self.requester.get_list('tables')


class RestTablesApi(TablesApi, TablesApiProvider):
    def __init__(self, requester: Requester):
        self.requester = requester
        self.raw_api = RawRestTablesApi(self.requester)

    @property
    def tables(self) -> TablesApi:
        return self

    @property
    def raw(self) -> RawTablesApi:
        return self.raw_api

    def get(self) -> list[Table]:
        return [t.to_table() for t in self.requester.get_tables()]

    def export(self, table_id: TableId) -> str:
        raise errors.NotImplementedErr()

    def get_partitions(self, table_id: TableId) -> list[TablePartition]:
        table = find_by_id(table_id, self.requester.get_tables())
        return [
            TablePartition(
                table_name=table.display_data.name,
                name=partition.name
            )
            for partition in table.partitions_columns
        ]
