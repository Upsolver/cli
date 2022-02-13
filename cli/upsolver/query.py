import time
from abc import ABCMeta, abstractmethod
from typing import Any, Optional

from cli.errors import Timeout, api_err_from_resp
from cli.upsolver.lexer import QueryLexer
from cli.upsolver.requester import BetterResponse, Requester


class QueryApi(metaclass=ABCMeta):
    ExecutionResult = list[dict[Any, Any]]

    @abstractmethod
    def execute(self, query: str) -> ExecutionResult:
        pass

    @abstractmethod
    def check_syntax(self, expression: str) -> list[str]:
        pass


class Drainer(object):
    def __init__(self,
                 requester: Requester,
                 wait_interval_sec: float = 0.5,
                 max_time_sec: Optional[float] = None):
        self.requester = requester
        self.wait_interval_sec = wait_interval_sec
        self.max_time_sec = max_time_sec

    def drain(self, resp: BetterResponse, time_spent_sec: float = 0) -> QueryApi.ExecutionResult:
        def raise_err() -> None:
            raise api_err_from_resp(resp)

        # TODO response is a list that always contains a single value?
        resp_json = resp.json()
        rjson = resp_json[0] if type(resp_json) is list else resp_json
        sc = resp.status_code
        if int(sc / 100) != 2:
            raise_err()

        status = rjson['status']
        is_success = sc == 200 and status == 'Success'

        # 201 is CREATED; returned on initial creation of "pending" response
        # 202 is ACCEPTED; returned if existing pending query is still not ready
        is_pending = (sc == 201 or sc == 202) and status == 'Pending'
        if not (is_success or is_pending):
            raise_err()

        if is_pending:
            while (self.max_time_sec is None) or time_spent_sec < self.max_time_sec:
                time.sleep(self.wait_interval_sec)
                return self.drain(
                    resp=self.requester.get(path=rjson['current']),
                    time_spent_sec=time_spent_sec + self.wait_interval_sec,
                )

            raise Timeout()

        result = rjson['result']
        grid = result['grid']  # columns, data, ...
        column_names = [c['name'] for c in grid['columns']]
        data_w_columns = [dict(zip(column_names, row)) for row in grid['data']]
        next_result: str = result.get('next')
        return data_w_columns + (
            [] if next_result is None
            else self.drain(
                resp=self.requester.get(path=next_result),
                time_spent_sec=time_spent_sec
            )
        )


class RestQueryApi(QueryApi):
    def __init__(self, requester: Requester, lexer: QueryLexer):
        self.requester = requester
        self.lexer = lexer

    def check_syntax(self, expression: str) -> list[str]:
        raise NotImplementedError()

    def execute(self, query: str) -> QueryApi.ExecutionResult:
        assert len(query) > 0
        drainer = Drainer(requester=self.requester, max_time_sec=10.0)
        results: list[tuple[str, QueryApi.ExecutionResult]] = []
        for q in self.lexer.split(query):
            results.append(
                (
                    q,
                    drainer.drain(self.requester.post('query', json={'sql': q}))
                )
            )

        if len(results) > 1:
            return [
                {'query': q, 'result': res}
                for (q, res) in results
            ]
        else:
            return results[0][1]
