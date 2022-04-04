from abc import ABCMeta, abstractmethod
from typing import Iterator

from cli.upsolver.entities import ExecutionResult
from cli.upsolver.poller import ResponsePoller
from cli.upsolver.requester import Requester


class QueryApi(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, query: str) -> Iterator[ExecutionResult]:
        """
        :param query: a singular SQL statement (i.e. multiple statements separated by ';' are not
        supported by this interface)
        :return: since queries may result in large responses, they are returned in chunks.
        """
        pass

    @abstractmethod
    def check_syntax(self, expression: str) -> list[str]:
        pass


class RestQueryApi(QueryApi):
    def __init__(self, requester: Requester, poller: ResponsePoller):
        self.requester = requester
        self.poller = poller

    def check_syntax(self, expression: str) -> list[str]:
        raise NotImplementedError()

    _NextResultPath = str  # results are paged, with "next pointer" being a path of url

    def execute(self, query: str) -> Iterator[ExecutionResult]:
        assert len(query) > 0

        (data, next_path) = self.poller(
            self.requester,
            self.requester.post('query', json={'sql': query})
        )
        yield data

        while next_path is not None:
            (data, next_path) = self.poller(self.requester, self.requester.get(next_path))
            yield data
