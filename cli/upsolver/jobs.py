from abc import ABCMeta, abstractmethod
from typing import Any

from cli import errors
from cli.upsolver.entities import Job
from cli.upsolver.requester import Requester


class RawJobsApi(metaclass=ABCMeta):
    @abstractmethod
    def get_jobs_raw(self) -> list[dict[Any, Any]]:
        pass


class JobsApi(RawJobsApi):
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

    def get_jobs_raw(self) -> list[dict[Any, Any]]:
        return self.requester.get_list('jobs')

    def export_job(self, job: str) -> str:
        resp = self.requester.get(f'inspections/describe/%2Fjobs%2F{job}')
        try:
            return resp.json()['sql']
        except Exception:
            raise errors.PayloadErr(resp, 'failed to extract sql statement')
