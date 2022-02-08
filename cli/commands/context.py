import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Optional

from click import echo
from prompt_toolkit.completion import Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import StyleAndTextTuples
from yarl import URL

from cli.config import (
    Config,
    ConfigurationManager,
    LogLvl,
    ProfileAuthSettings,
    get_auth_settings,
)
from cli.errors import ConfigErr
from cli.upsolver.api import UpsolverApi
from cli.upsolver.auth import AuthApi, InvalidAuthApi, RestAuthApi
from cli.upsolver.catalogs import CatalogsApi, RestCatalogsApi
from cli.upsolver.clusters import ClustersApi, RestClustersApi
from cli.upsolver.entities import Catalog, Cluster, Job, Table, TablePartition
from cli.upsolver.jobs import JobsApi, RestJobsApi
from cli.upsolver.lexer import SimpleQueryLexer
from cli.upsolver.lsp import FakeLspApi, LspApi
from cli.upsolver.query import QueryApi, RestQueryApi
from cli.upsolver.requester import Requester, TokenAuthFiller
from cli.upsolver.tables import RestTablesApi, TablesApi


class CliContext(object):
    """
    This is used as the value for click.Context object that is passed to subcommands.

    CliContext holds "global" information (e.g. configuration) and is capable of spawning
    entities that depend on this configuration (e.g. upsolver upsolver).

    Also serves as the builder of UpsolverApi from more basic api components.

    Reasoning for having two builder methods, one for auth api and another for whole upsolver api:
    all api components depend on authentication api, and so we need to instantiate it before all
    others and use it, and with the results of calling it we are able to construct the other
    components.
    """

    def _setup_logging(self, conf: Config) -> None:
        self.log = logging.getLogger('CLI')

        lvl = (
            LogLvl.DEBUG if conf.debug
            else (conf.options.log_level if conf.options is not None else LogLvl.CRITICAL)
        ).to_logging()
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')

        handlers: list[logging.Handler] = []
        if conf.options is not None:
            handlers.append(RotatingFileHandler(
                filename=conf.options.log_file,
                maxBytes=10 * (2 ** 20),
            ))

        # if debug mode, also write to stderr
        if conf.debug:
            handlers.append(logging.StreamHandler())

        for h in handlers:
            h.setLevel(lvl)
            h.setFormatter(formatter)
            self.log.addHandler(h)

    def __init__(self, confman: ConfigurationManager):
        self.confman = confman
        self._setup_logging(self.confman.conf)

    def auth_api(self, auth_base_url: Optional[URL] = None) -> AuthApi:
        if auth_base_url is None:
            auth_base_url = ConfigurationManager.CLI_DEFAULT_BASE_URL
        assert auth_base_url.is_absolute()

        return RestAuthApi(auth_base_url)

    def upsolver_api(self) -> UpsolverApi:
        auth_settings: Optional[ProfileAuthSettings] = \
            get_auth_settings(self.confman.conf.active_profile)

        if auth_settings is None:
            raise ConfigErr('could not find authentication settings, please use the '
                            '`configure` sub-command to generate them.')

        requester = Requester(
            base_url=Requester.get_base_url(auth_settings.base_url, auth_settings.token),
            auth_filler=TokenAuthFiller(auth_settings.token)
        )

        auth: AuthApi = InvalidAuthApi()
        clusters: ClustersApi = RestClustersApi(requester)
        catalogs: CatalogsApi = RestCatalogsApi(requester)
        jobs: JobsApi = RestJobsApi(requester)
        tables: TablesApi = RestTablesApi(requester)
        queries: QueryApi = RestQueryApi(requester, SimpleQueryLexer())
        lsp: LspApi = FakeLspApi()  # TODO

        class UpsolverApiImpl(UpsolverApi):
            def get_completions(self, doc: Document) -> list[Completion]:
                return lsp.get_completions(doc)

            def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
                return lsp.lex_document(document)

            def check_syntax(self, expression: str) -> list[str]:
                return queries.check_syntax(expression)

            def execute(self, query: str) -> list[dict[Any, Any]]:
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

            def stop_cluster(self, cluster: str) -> Optional[str]:
                return clusters.stop_cluster(cluster)

            def run_cluster(self, cluster: str) -> Optional[str]:
                return clusters.run_cluster(cluster)

            def delete_cluster(self, cluster: str) -> Optional[str]:
                return clusters.delete_cluster(cluster)

            def get_clusters(self) -> list[Cluster]:
                return clusters.get_clusters()

            def authenticate(self, email: str, password: str) -> ProfileAuthSettings:
                return auth.authenticate(email, password)

        return UpsolverApiImpl()

    def write(self, x: Any) -> None:
        echo(message=self.confman.get_formatter()(x), file=sys.stdout)

    def echo(self, msg: str) -> None:
        echo(msg)
