from abc import ABCMeta, abstractmethod
from typing import Iterator

from cli.upsolver.entities import ExecutionResult
from cli.upsolver.poller import ResponsePollerBuilder
from cli.upsolver.requester import Requester


class QueryApi(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, query: str, timeout_sec: float) -> Iterator[ExecutionResult]:
        """
        :param query: a SQL statement
        :return: since queries may result in large responses, they are returned in chunks.
        """
        pass

    @abstractmethod
    def check_syntax(self, expression: str) -> list:
        pass


class RestQueryApi(QueryApi):
    def __init__(self, requester: Requester, poller_builder: ResponsePollerBuilder):
        self.requester = requester
        self.poller_builder = poller_builder

    def check_syntax(self, expression: str) -> list:
        raise NotImplementedError()

    _NextResultPath = str  # results are paged, with "next pointer" being a path of url

    def execute(self, query: str, timeout_sec: float) -> Iterator[ExecutionResult]:
        assert len(query) > 0
        poller = self.poller_builder(timeout_sec)

        (data, next_path) = poller(
            self.requester,
            self.requester.post('query', json={'sql': query})
        )
        yield data

        while next_path is not None:
            (data, next_path) = poller(self.requester, self.requester.get(next_path))
            yield data
