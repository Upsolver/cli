from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Optional

from cli.errors import ApiErr, ClusterNotFound
from cli.upsolver.entities import Cluster
from cli.upsolver.requester import Requester


class ClustersApi(metaclass=ABCMeta):
    @abstractmethod
    def get_clusters(self) -> list[Cluster]:
        pass

    @abstractmethod
    def export_cluster(self, cluster: str) -> str:
        pass

    @abstractmethod
    def stop_cluster(self, cluster: str) -> Optional[str]:
        pass

    @abstractmethod
    def run_cluster(self, cluster: str) -> Optional[str]:
        pass

    @abstractmethod
    def delete_cluster(self, cluster: str) -> Optional[str]:
        pass


class RestClustersApi(ClustersApi):
    def __init__(self, requester: Requester):
        self.requester = requester

    def _get_cluster_id(self, cluster: str) -> str:
        available_clusters = self.get_clusters()
        for c in available_clusters:
            if c.name == cluster:
                return c.id

        raise ClusterNotFound(cluster, available_clusters)

    @staticmethod
    def _handle_exceptions(operation: Callable[[], Any]) -> Optional[str]:
        try:
            operation()
        except ClusterNotFound as ex:
            return f'Failed to find cluster named \'{ex.cluster_name}\' among the following ' \
                   f'list of clusters: {",".join([c.name for c in ex.existing_clusters])}'
        except ApiErr as ex:
            return ex.detail_message()

        return None

    def get_clusters(self) -> list[Cluster]:
        environments = [
            dashboard_ele['environment']
            for dashboard_ele in self.requester.get('environments/dashboard').json()
        ]

        return [
            Cluster(
                name=env['displayData']['name'],
                id=env['id'],
                running=env['running']
            )
            for env in environments
        ]

    def export_cluster(self, cluster: str) -> str:
        raise NotImplementedError()

    def stop_cluster(self, cluster: str) -> Optional[str]:
        """
        :return: A string detailing an error, or None if there were no errors
        """
        return self._handle_exceptions(
            lambda: self.requester.put(f'environments/stop/{self._get_cluster_id(cluster)}')
        )

    def run_cluster(self, cluster: str) -> Optional[str]:
        """
        :return: A string detailing an error, or None if there were no errors
        """
        return self._handle_exceptions(
            lambda: self.requester.put(f'environments/run/{self._get_cluster_id(cluster)}')
        )

    def delete_cluster(self, cluster: str) -> Optional[str]:
        """
        :return: A string detailing an error, or None if there were no errors
        """
        return self._handle_exceptions(
            lambda: self.requester.patch(
                path=f'environments/{self._get_cluster_id(cluster)}',
                json={'clazz': 'DeleteEnvironment'}
            )
        )
