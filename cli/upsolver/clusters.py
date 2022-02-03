from abc import ABCMeta, abstractmethod
from typing import Optional

from cli.errors import BadArgument
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
        self.requester.put(f'environments/stop/{cluster}')
        return None  # TODO currently the call to put throws the error...

    def run_cluster(self, cluster: str) -> Optional[str]:
        """
        :return: A string detailing an error, or None if there were no errors
        """
        self.requester.put(f'environments/run/{cluster}')
        return None  # TODO currently the call to put throws the error...

    def delete_cluster(self, cluster: str) -> Optional[str]:
        """
        :return: A string detailing an error, or None if there were no errors
        """
        for c in self.get_clusters():
            if c.name == cluster:
                delete_resp = self.requester.patch(
                    path=f'environments/{c.id}',
                    json={'clazz': 'DeleteEnvironment'}
                )

                if delete_resp.status_code != 200:
                    return f'Failed to delete cluster "{cluster}": {delete_resp.json()}'

                return None

        raise BadArgument(f'Could not find cluster named "{cluster}"')
