import time
from typing import Callable, Optional

from cli import errors
from cli.upsolver.entities import ExecutionResult, NextResultPath
from cli.upsolver.requester import Requester
from cli.upsolver.response import UpsolverResponse

"""
Polling is performed on responses that are "pending": we don't know when the results will be
available and so the Poller's job is to wait until the results are ready.

inputs:
- a Requester is required to make further requests (i.e. to poll).
- UpsolverResponse object is the initial response the poller will try to get the results of.

outputs:
- ExecutionResult is the result for the initial response given in the inputs
- an optional NextResultPath that can be queried for further results (e.g. when performing a
  SELECT the response mayb have multiple parts).
"""
ResponsePoller = Callable[
    [Requester, UpsolverResponse],
    tuple[ExecutionResult, Optional[NextResultPath]]
]


class SimpleResponsePoller(object):
    def __init__(self,
                 wait_interval_sec: float = 0.5,
                 max_time_sec: Optional[float] = 10.0):
        self.wait_interval_sec = wait_interval_sec
        self.max_time_sec = max_time_sec

    def _get_result_helper(self,
                           requester: Requester,
                           resp: UpsolverResponse,
                           start_time: float = 0) -> \
            tuple[ExecutionResult, Optional[NextResultPath]]:
        """
        :param start_time: time (in seconds since the Epoch) at which polling has started.
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
            time_spent_sec = int(time.time() - start_time)
            if (self.max_time_sec is not None) and (time_spent_sec >= self.max_time_sec):
                raise errors.PendingResultTimeout(resp)

            time.sleep(self.wait_interval_sec)
            return self._get_result_helper(
                requester=requester,
                resp=requester.get(path=rjson['current']),
                start_time=start_time,
            )

        result = rjson['result']
        grid = result['grid']  # columns, data, ...
        column_names = [c['name'] for c in grid['columns']]
        data_w_columns: ExecutionResult = [dict(zip(column_names, row)) for row in grid['data']]

        return data_w_columns, result.get('next')

    def __call__(self, requester: Requester, resp: UpsolverResponse) -> \
            tuple[ExecutionResult, Optional[NextResultPath]]:
        """
        Waits until result data is ready and returns it (a response may contain actual data, or
        alternatively be a pending response which means we should ask for the results at some
        later, inderteminate, time).

        If the second returned value is not None, it means there is more result data that can
        be delivered, and can be retrieved using the returned path.
        """
        return self._get_result_helper(requester, resp, start_time=time.time())
