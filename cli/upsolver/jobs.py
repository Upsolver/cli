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
        return [ji.to_job() for ji in self.requester.get_jobs()]

    def export_job(self, job: str) -> str:
        raise NotImplementedError()
