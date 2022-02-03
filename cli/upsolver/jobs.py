from abc import ABCMeta, abstractmethod

from cli.upsolver.entities import Job
from cli.upsolver.requester import Requester


class JobsApi(metaclass=ABCMeta):
    @abstractmethod
    def get_jobs(self) -> list[Job]:
        pass

    @abstractmethod
    def export_job(self, job: str) -> str:
        pass


class RestJobsApi(JobsApi):
    def __init__(self, requester: Requester):
        self.requester = requester

    def get_jobs(self) -> list[Job]:
        return [
            Job(name=j['displayData']['name'], status=j['status'])
            for j in self.requester.get('jobs').json()['jobs']
        ]

    def export_job(self, job: str) -> str:
        raise NotImplementedError()
