from abc import ABC, abstractmethod
from typing import Any

from cli import errors
from cli.upsolver.entities import Catalog
from cli.upsolver.requester import Requester
from cli.utils import find_by_id

CatalogId = str


class RawCatalogsApi(ABC):
    @abstractmethod
    def get(self) -> list[dict[Any, Any]]:
        pass


class RawCatalogsApiProvider(ABC):
    @property
    @abstractmethod
    def raw(self) -> RawCatalogsApi:
        pass


class CatalogsApi(RawCatalogsApiProvider):
    @abstractmethod
    def get(self) -> list[Catalog]:
        pass

    @abstractmethod
    def export(self, catalog_id: CatalogId) -> str:
        pass


class CatalogsApiProvider(ABC):
    @property
    @abstractmethod
    def catalogs(self) -> CatalogsApi:
        pass


class RawRestCatalogsApi(RawCatalogsApi):
    def __init__(self, requester: Requester):
        self.requester = requester

    def get(self) -> list[dict[Any, Any]]:
        return self.requester.get_list('connections')


class RestCatalogsApi(CatalogsApi, CatalogsApiProvider):
    def __init__(self, requester: Requester):
        self.requester = requester
        self.raw_api = RawRestCatalogsApi(self.requester)

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

    @property
    def catalogs(self) -> CatalogsApi:
        return self

    @property
    def raw(self) -> RawCatalogsApi:
        return self.raw_api

    def get(self) -> list[Catalog]:
        return [c.to_catalog() for c in self.requester.get_connections()]

    def export(self, catalog_id: CatalogId) -> str:
        c = find_by_id(catalog_id, self.requester.get_connections())
        resp = self.requester.get(
            f'inspections/describe/%2Fconnections'
            f'%2F{self._connection_kind_to_inspection_name(c.connection.kind)}'
            f'%2F{c.id}'
        )

        try:
            return resp.json()['sql']
        except Exception:
            raise errors.PayloadErr(resp, 'failed to extract sql statement')
