import builtins
from abc import ABC, abstractmethod

from cli import errors
from cli.upsolver.raw_entities import JobInfo
from cli.upsolver.requester import Requester
from cli.utils import from_dict

JobId = str


class RawJobsApi(ABC):
    @abstractmethod
    def list(self) -> list:
        pass

    def list_jobs_info(self) -> builtins.list:
        return [from_dict(JobInfo, ji) for ji in self.list()]


class RawJobsApiProvider(ABC):
    @property
    @abstractmethod
    def raw(self) -> RawJobsApi:
        pass


class JobsApi(RawJobsApiProvider):
    def list(self) -> list:
        return [ji.to_api_entity() for ji in self.raw.list_jobs_info()]

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

    def list(self) -> list:
        return self.requester.get_list('jobs', list_field_name='jobs')


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

    def export(self, job_id: JobId) -> str:
        resp = self.requester.get(f'inspections/describe/%2Fjobs%2F{job_id}')
        try:
            return resp.json()['sql']
        except Exception:
            raise errors.PayloadErr(resp, 'failed to extract sql statement')
