from typing import Callable, Iterator

from prompt_toolkit.completion import Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import StyleAndTextTuples

from cli.config import ProfileAuthSettings
from cli.upsolver.api import UpsolverApi
from cli.upsolver.auth import AuthApi, InvalidAuthApi
from cli.upsolver.catalogs import CatalogsApi, RestCatalogsApi
from cli.upsolver.clusters import ClustersApi, RestClustersApi
from cli.upsolver.entities import Catalog, Cluster, ExecutionResult, Job, Table, TablePartition
from cli.upsolver.jobs import JobsApi, RestJobsApi
from cli.upsolver.lsp import FakeLspApi, LspApi
from cli.upsolver.poller import SimpleResponsePoller
from cli.upsolver.query import QueryApi, RestQueryApi
from cli.upsolver.requester import Requester
from cli.upsolver.tables import RestTablesApi, TablesApi


def build_upsolver_api(requester: Requester) -> UpsolverApi:
    """
    Given a Requester object (a wrapper around requests package that handles issuing http
    requests to Upsolvers REST Api) returns an implementation of the UpsolverApi interface.
    """

    auth: AuthApi = InvalidAuthApi()  # i.e. should not be used.
    clusters: ClustersApi = RestClustersApi(requester)
    catalogs: CatalogsApi = RestCatalogsApi(requester)
    jobs: JobsApi = RestJobsApi(requester)
    tables: TablesApi = RestTablesApi(requester)
    queries: QueryApi = RestQueryApi(requester, SimpleResponsePoller())
    lsp: LspApi = FakeLspApi()

    class UpsolverApiImpl(UpsolverApi):
        def get_completions(self, doc: Document) -> list[Completion]:
            return lsp.get_completions(doc)

        def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
            return lsp.lex_document(document)

        def check_syntax(self, expression: str) -> list[str]:
            return queries.check_syntax(expression)

        def execute(self, query: str) -> Iterator[ExecutionResult]:
            return queries.execute(query)

        def get_tables(self) -> list[Table]:
            return tables.get_tables()

        def export_table(self, table: str) -> str:
            return tables.export_table(table)

        def get_table_partitions(self, table: str) -> list[TablePartition]:
            return tables.get_table_partitions(table)

        def get_catalogs(self) -> list[Catalog]:
            return catalogs.get_catalogs()

        def export_catalog(self, catalog: str) -> str:
            return catalogs.export_catalog(catalog)

        def get_jobs(self) -> list[Job]:
            return jobs.get_jobs()

        def export_job(self, job: str) -> str:
            return jobs.export_job(job)

        def export_cluster(self, cluster: str) -> str:
            return clusters.export_cluster(cluster)

        def stop_cluster(self, cluster: str) -> None:
            clusters.stop_cluster(cluster)

        def run_cluster(self, cluster: str) -> None:
            clusters.run_cluster(cluster)

        def delete_cluster(self, cluster: str) -> None:
            clusters.delete_cluster(cluster)

        def get_clusters(self) -> list[Cluster]:
            return clusters.get_clusters()

        def authenticate(self, email: str, password: str) -> ProfileAuthSettings:
            return auth.authenticate(email, password)

    return UpsolverApiImpl()
