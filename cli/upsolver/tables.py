from abc import ABCMeta, abstractmethod
from typing import Any

from cli import errors
from cli.upsolver.entities import Table, TablePartition
from cli.upsolver.requester import Requester


class RawTablesApi(metaclass=ABCMeta):
    @abstractmethod
    def get_tables_raw(self) -> list[dict[Any, Any]]:
        pass


class TablesApi(RawTablesApi):
    @abstractmethod
    def get_tables(self) -> list[Table]:
        pass

    @abstractmethod
    def export_table(self, table: str) -> str:
        pass

    @abstractmethod
    def get_table_partitions(self, table: str) -> list[TablePartition]:
        pass


class RestTablesApi(TablesApi):
    def __init__(self, requester: Requester):
        self.requester = requester

    def get_tables(self) -> list[Table]:
        return [t.to_table() for t in self.requester.get_tables()]

    def get_tables_raw(self) -> list[dict[Any, Any]]:
        return self.requester.get_list('tables')

    def export_table(self, table: str) -> str:
        raise errors.NotImplementedErr()

    def get_table_partitions(self, table: str) -> list[TablePartition]:
        for raw_table in self.requester.get_tables():
            if raw_table.display_data.name == table:
                return [
                    TablePartition(
                        table_name=raw_table.display_data.name,
                        name=partition.name
                    )
                    for partition in raw_table.partitions_columns
                ]

        return []  # didn't find a table with a matching name
