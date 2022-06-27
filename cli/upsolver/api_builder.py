from typing import Any, cast

from cli.upsolver.api import UpsolverApi
from cli.upsolver.auth import InvalidAuthApi
from cli.upsolver.catalogs import RestCatalogsApi
from cli.upsolver.clusters import RestClustersApi
from cli.upsolver.jobs import RestJobsApi
from cli.upsolver.lsp import FakeLspApi
from cli.upsolver.poller import SimpleResponsePoller
from cli.upsolver.query import RestQueryApi
from cli.upsolver.requester import Requester
from cli.upsolver.tables import RestTablesApi
from cli.upsolver.worksheets import RestWorksheetsApi


def build_upsolver_api(requester: Requester) -> UpsolverApi:
    """
    Given a Requester object (a wrapper around requests package that handles issuing http
    requests to Upsolvers REST Api) returns an implementation of the UpsolverApi interface.
    """

    api_objs = [
        InvalidAuthApi(),  # i.e. should not be used.
        RestClustersApi(requester),
        RestCatalogsApi(requester),
        RestJobsApi(requester),
        RestTablesApi(requester),
        RestQueryApi(requester, lambda timeout_sec: SimpleResponsePoller(max_time_sec=timeout_sec)),
        FakeLspApi(),
        RestWorksheetsApi(requester)
    ]

    class UpsolverApiImpl:
        def __getattr__(self, attr: Any) -> Any:
            for ao in api_objs:
                try:
                    return getattr(ao, attr)
                except AttributeError:
                    continue

            raise AttributeError(f'API implementation has no attribute {attr}')

    return cast(UpsolverApi, UpsolverApiImpl())
