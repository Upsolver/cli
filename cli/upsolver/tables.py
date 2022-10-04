import builtins
from abc import ABC, abstractmethod

from cli import errors
from cli.upsolver import raw_entities
from cli.upsolver.entities import TablePartition
from cli.upsolver.requester import Requester
from cli.utils import find_by_id, from_dict

TableId = str


class RawTablesApi(ABC):
    @abstractmethod
    def list(self) -> list:
        pass

    def list_tables(self) -> builtins.list:
        return [from_dict(raw_entities.Table, t) for t in self.list()]


class RawTablesApiProvider(ABC):
    @property
    @abstractmethod
    def raw(self) -> RawTablesApi:
        pass


class TablesApi(RawTablesApiProvider):
    def list(self) -> list:
        return [t.to_api_entity() for t in self.raw.list_tables()]

    @abstractmethod
    def export(self, table_id: TableId) -> str:
        pass

    @abstractmethod
    def get_partitions(self, table_id: TableId) -> builtins.list:
        pass


class TablesApiProvider(ABC):
    @property
    @abstractmethod
    def tables(self) -> TablesApi:
        pass


class RawRestTablesApi(RawTablesApi):
    def __init__(self, requester: Requester):
        self.requester = requester

    def list(self) -> list:
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

    def export(self, table_id: TableId) -> str:
        raise errors.NotImplementedErr()

    def get_partitions(self, table_id: TableId) -> list:
        table = find_by_id(table_id, self.raw.list_tables())
        return [
            TablePartition(
                table_name=table.display_data.name,
                name=partition.name
            )
            for partition in table.partitions_columns
        ]
