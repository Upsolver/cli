from abc import ABC, abstractmethod
from typing import Any

from cli import errors
from cli.upsolver.entities import Cluster
from cli.upsolver.requester import Requester

ClusterId = str


class RawClustersApi(ABC):
    @abstractmethod
    def get(self) -> list[dict[Any, Any]]:
        pass


class RawClustersApiProvider(ABC):
    @property
    @abstractmethod
    def raw(self) -> RawClustersApi:
        pass


class ClustersApi(RawClustersApiProvider):
    @abstractmethod
    def get(self) -> list[Cluster]:
        pass

    @abstractmethod
    def stop(self, cluster_id: ClusterId) -> None:
        pass

    @abstractmethod
    def run(self, cluster_id: ClusterId) -> None:
        pass

    @abstractmethod
    def delete(self, cluster_id: ClusterId) -> None:
        pass


class ClustersApiProvider(ABC):
    @property
    @abstractmethod
    def clusters(self) -> ClustersApi:
        pass


class RawRestClustersApi(RawClustersApi):
    def __init__(self, requester: Requester):
        self.requester = requester

    def get(self) -> list[dict[Any, Any]]:
        return self.requester.get_list('environments/dashboard')


class RestClustersApi(ClustersApi, ClustersApiProvider):
    def __init__(self, requester: Requester):
        self.requester = requester
        self.raw_api = RawRestClustersApi(self.requester)

    def _get_cluster_id(self, cluster_name: str) -> str:
        available_clusters = self.get()
        for c in available_clusters:
            if c.name == cluster_name:
                return c.id

        raise errors.EntityNotFound(cluster_name, [c.name for c in available_clusters])

    @property
    def clusters(self) -> ClustersApi:
        return self

    @property
    def raw(self) -> RawClustersApi:
        return self.raw_api

    def get(self) -> list[Cluster]:
        return [env.to_cluster() for env in self.requester.get_environments()]

    def stop(self, cluster_id: ClusterId) -> None:
        self.requester.put(f'environments/stop/{self._get_cluster_id(cluster_id)}')

    def run(self, cluster_id: ClusterId) -> None:
        self.requester.put(f'environments/run/{self._get_cluster_id(cluster_id)}')

    def delete(self, cluster_id: ClusterId) -> None:
        self.requester.patch(
            path=f'environments/{self._get_cluster_id(cluster_id)}',
            json={'clazz': 'DeleteEnvironment'}
        )
