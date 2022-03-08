import time
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Iterator, Optional

from cli import errors
from cli.upsolver.requester import BetterResponse, Requester

ExecutionResult = list[dict[Any, Any]]
ExecutionErr = Exception
NextResultPath = str  # results are paged, with "next pointer" being a path of url


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


ResponsePoller = Callable[
    [Requester, BetterResponse],
    tuple[ExecutionResult, Optional[NextResultPath]]
]


class SimpleResponsePoller(object):
    """
    Polling is performed on responses that are "pending": we don't know when the results will be
    available and so the Poller's job is to wait until the results are ready.
    """
    def __init__(self,
                 wait_interval_sec: float = 0.5,
                 max_time_sec: Optional[float] = 10.0):
        self.wait_interval_sec = wait_interval_sec
        self.max_time_sec = max_time_sec

    def _get_result_helper(self,
                           requester: Requester,
                           resp: BetterResponse,
                           time_spent_sec: float = 0) -> \
            tuple[ExecutionResult, Optional[NextResultPath]]:
        """
        :param time_spent_sec: this method is called recursively, with time_spent_sec parameter
          accumulating total time spent waiting for the response to become "ready" (i.e. to get a
          response with actual data).
        """
        def raise_err() -> None:
            raise errors.ApiErr(resp)

        sc = resp.status_code
        if int(sc / 100) != 2:
            raise_err()

        resp_json = resp.json()
        rjson = resp_json[0] if type(resp_json) is list else resp_json

        status = rjson['status']
        is_success = sc == 200 and status == 'Success'

        # 201 is CREATED; returned on initial creation of "pending" response
        # 202 is ACCEPTED; returned if existing pending query is still not ready
        is_pending = (sc == 201 or sc == 202) and status == 'Pending'

        if not (is_success or is_pending):
            raise_err()

        if is_pending:
            if (self.max_time_sec is not None) and (time_spent_sec >= self.max_time_sec):
                raise errors.PendingResultTimeout(resp)

            time.sleep(self.wait_interval_sec)
            return self._get_result_helper(
                requester=requester,
                resp=requester.get(path=rjson['current']),
                time_spent_sec=time_spent_sec + self.wait_interval_sec,
            )

        result = rjson['result']
        grid = result['grid']  # columns, data, ...
        column_names = [c['name'] for c in grid['columns']]
        data_w_columns: ExecutionResult = [dict(zip(column_names, row)) for row in grid['data']]

        return data_w_columns, result.get('next')

    def __call__(self, requester: Requester, resp: BetterResponse) -> \
            tuple[ExecutionResult, Optional[NextResultPath]]:
        """
        Waits until result data is ready and returns it (a response may contain actual data, or
        alternatively be a pending response which means we should ask for the results at some
        later, inderteminate, time).

        If the second returned value is not None, it means there is more result data that can
        be delivered, and can be retrieved using the returned path.
        """
        return self._get_result_helper(requester, resp)


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
