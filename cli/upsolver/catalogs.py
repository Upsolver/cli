from abc import ABCMeta, abstractmethod

from cli.upsolver.entities import Catalog
from cli.upsolver.requester import Requester


class CatalogsApi(metaclass=ABCMeta):
    @abstractmethod
    def get_catalogs(self) -> list[Catalog]:
        pass

    @abstractmethod
    def export_catalog(self, catalog: str) -> str:
        pass


class RestCatalogsApi(CatalogsApi):
    def __init__(self, requester: Requester):
        self.requester = requester

    def get_catalogs(self) -> list[Catalog]:
        return [
            Catalog(
                id=c['id'],
                name=c['connection']['displayData']['name'],
                created_by=c['connection']['displayData'].get('createdBy'),
                kind=c['connection']['clazz'],
                orgId=c['organizationId'],
            )
            for c in self.requester.get('connections').json()
        ]

    def export_catalog(self, catalog: str) -> str:
        raise NotImplementedError()
