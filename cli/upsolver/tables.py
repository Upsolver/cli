from abc import ABCMeta, abstractmethod

from cli import errors
from cli.upsolver.entities import Table, TablePartition
from cli.upsolver.requester import Requester


class TablesApi(metaclass=ABCMeta):
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
        return [
            Table(
                id=raw_table['id'],
                name=raw_table['displayData']['name']
            )
            for raw_table in self.requester.get('tables').json()
        ]

    def export_table(self, table: str) -> str:
        raise errors.NotImplementedErr()

    def get_table_partitions(self, table: str) -> list[TablePartition]:
        for raw_table in self.requester.get('tables').json():
            if raw_table['displayData']['name'] == table:
                return [
                    TablePartition(
                        table_name=raw_table['displayData']['name'],
                        name=partition['name']
                    )
                    for partition in raw_table['partitionColumns']
                ]

        return []  # didn't find a table with a matching name
