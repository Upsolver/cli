import builtins
from abc import ABC, abstractmethod
from typing import Any

from cli.upsolver.entities import Cluster
from cli.upsolver.raw_entities import EnvironmentDashboardResponse
from cli.upsolver.requester import Requester
from cli.utils import from_dict

ClusterId = str


class RawClustersApi(ABC):
    @abstractmethod
    def list(self) -> list[dict[str, Any]]:
        pass

    def list_environments(self) -> builtins.list[EnvironmentDashboardResponse]:
        return [from_dict(EnvironmentDashboardResponse, e) for e in self.list()]


class RawClustersApiProvider(ABC):
    @property
    @abstractmethod
    def raw(self) -> RawClustersApi:
        pass


class ClustersApi(RawClustersApiProvider):
    def list(self) -> list[Cluster]:
        return [env.to_api_entity() for env in self.raw.list_environments()]

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

    def list(self) -> list[dict[str, Any]]:
        return self.requester.get_list('environments/dashboard')


class RestClustersApi(ClustersApi, ClustersApiProvider):
    def __init__(self, requester: Requester):
        self.requester = requester
        self.raw_api = RawRestClustersApi(self.requester)

    @property
    def clusters(self) -> ClustersApi:
        return self

    @property
    def raw(self) -> RawClustersApi:
        return self.raw_api

    def stop(self, cluster_id: ClusterId) -> None:
        self.requester.put(f'environments/stop/{cluster_id}')

    def run(self, cluster_id: ClusterId) -> None:
        self.requester.put(f'environments/run/{cluster_id}')

    def delete(self, cluster_id: ClusterId) -> None:
        self.requester.patch(
            path=f'environments/{cluster_id}',
            json={'clazz': 'DeleteEnvironment'}
        )
