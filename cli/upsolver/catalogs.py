from abc import ABCMeta, abstractmethod
from typing import Any

from cli import errors
from cli.upsolver.entities import Catalog
from cli.upsolver.requester import Requester


class RawCatalogsApi(metaclass=ABCMeta):
    @abstractmethod
    def get_catalogs_raw(self) -> list[dict[Any, Any]]:
        pass


class CatalogsApi(RawCatalogsApi):
    @abstractmethod
    def get_catalogs(self) -> list[Catalog]:
        pass

    @abstractmethod
    def export_catalog(self, catalog: str) -> str:
        pass


class RestCatalogsApi(CatalogsApi):
    def __init__(self, requester: Requester):
        self.requester = requester

    @staticmethod
    def _connection_kind_to_inspection_name(kind: str) -> str:
        simple_kinds = [
            's3', 'athena', 'snowflake', 'redshift', 'mysql', 'mssql', 'synapse',
            'postgres', 'kafka', 'kinesis',
        ]

        other_kinds = [
            ('elastic', 'elastic-search'), ('event', 'event-hub')
        ]

        kind = kind.lower()
        for sk in simple_kinds:
            if sk in kind:
                return sk

        for key, res in other_kinds:
            if key in kind:
                return res

        return kind  # default to just returning the kind as is

    def get_catalogs(self) -> list[Catalog]:
        return [c.to_catalog() for c in self.requester.get_connections()]

    def get_catalogs_raw(self) -> list[dict[Any, Any]]:
        return self.requester.get_list('connections')

    def export_catalog(self, catalog: str) -> str:
        connections = self.requester.get_connections()
        for c in connections:
            if c.connection.display_data.name == catalog:
                resp = self.requester.get(
                    f'inspections/describe/%2Fconnections'
                    f'%2F{self._connection_kind_to_inspection_name(c.connection.kind)}'
                    f'%2F{c.id}'
                )

                try:
                    return resp.json()['sql']
                except Exception:
                    raise errors.PayloadErr(resp, 'failed to extract sql statement')
        raise errors.EntityNotFound(catalog, [c.connection.display_data.name for c in connections])
