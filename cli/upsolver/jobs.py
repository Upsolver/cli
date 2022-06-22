from abc import ABC, abstractmethod
from typing import Any

from cli import errors
from cli.upsolver.entities import Job
from cli.upsolver.requester import Requester

JobId = str


class RawJobsApi(ABC):
    @abstractmethod
    def get(self) -> list[dict[Any, Any]]:
        pass


class RawJobsApiProvider(ABC):
    @property
    @abstractmethod
    def raw(self) -> RawJobsApi:
        pass


class JobsApi(RawJobsApiProvider):
    @abstractmethod
    def get(self) -> list[Job]:
        pass

    @abstractmethod
    def export(self, job_id: JobId) -> str:
        pass


class JobsApiProvider(ABC):
    @property
    @abstractmethod
    def jobs(self) -> JobsApi:
        pass


class RawRestJobsApi(RawJobsApi):
    def __init__(self, requester: Requester):
        self.requester = requester

    def get(self) -> list[dict[Any, Any]]:
        return self.requester.get_list('jobs')


class RestJobsApi(JobsApi, JobsApiProvider):
    def __init__(self, requester: Requester):
        self.requester = requester
        self.raw_api = RawRestJobsApi(self.requester)

    @property
    def jobs(self) -> JobsApi:
        return self

    @property
    def raw(self) -> RawJobsApi:
        return self.raw_api

    def get(self) -> list[Job]:
        return [ji.to_job() for ji in self.requester.get_jobs()]

    def export(self, job_id: JobId) -> str:
        resp = self.requester.get(f'inspections/describe/%2Fjobs%2F{job_id}')
        try:
            return resp.json()['sql']
        except Exception:
            raise errors.PayloadErr(resp, 'failed to extract sql statement')
