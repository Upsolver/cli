from abc import ABC

from cli.upsolver.auth import AuthApi
from cli.upsolver.catalogs import CatalogsApi
from cli.upsolver.clusters import ClustersApi
from cli.upsolver.jobs import JobsApi
from cli.upsolver.lsp import LspApi
from cli.upsolver.query import QueryApi
from cli.upsolver.tables import TablesApi


class UpsolverApi(
    AuthApi,
    ClustersApi,
    CatalogsApi,
    JobsApi,
    TablesApi,
    QueryApi,
    LspApi,
    ABC
):
    pass
