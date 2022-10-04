import builtins
from abc import ABC, abstractmethod

from cli import errors
from cli.upsolver.raw_entities import ConnectionInfo
from cli.upsolver.requester import Requester
from cli.utils import find_by_id, from_dict

CatalogId = str


class RawCatalogsApi(ABC):
    @abstractmethod
    def list(self) -> list:
        pass

    def list_connections_info(self) -> builtins.list:
        return [from_dict(ConnectionInfo, ci) for ci in self.list()]


class RawCatalogsApiProvider(ABC):
    @property
    @abstractmethod
    def raw(self) -> RawCatalogsApi:
        pass


class CatalogsApi(RawCatalogsApiProvider):
    def list(self) -> list:
        return [ci.to_api_entity() for ci in self.raw.list_connections_info()]

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

    def list(self) -> list:
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

    def export(self, catalog_id: CatalogId) -> str:
        c = find_by_id(catalog_id, self.list())
        resp = self.requester.get(
            f'inspections/describe/%2Fconnections'
            f'%2F{self._connection_kind_to_inspection_name(c.kind)}'
            f'%2F{c.id}'
        )

        try:
            return resp.json()['sql']
        except Exception:
            raise errors.PayloadErr(resp, 'failed to extract sql statement')
