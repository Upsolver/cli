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
        return [c.to_catalog() for c in self.requester.get_connections()]

    def export_catalog(self, catalog: str) -> str:
        raise NotImplementedError()
