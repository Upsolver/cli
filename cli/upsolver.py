import datetime
import time
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Iterable, NamedTuple, Optional

import requests
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.lexers import Lexer
from requests import Response

from cli.config import ProfileAuthSettings
from cli.errors import ApiErr, BadConfig

# TODO
#   - [ ] abstract class, implementations: actual, mock (tests, mocking lib for python?), local
#   - [ ] retries? timeouts?


class Cluster(NamedTuple):
    name: str
    id: str


class Catalog(NamedTuple):
    id: str
    name: str
    created_by: Optional[str]
    kind: str
    orgId: str


class Table(NamedTuple):
    name: str


class TablePartition(NamedTuple):
    table_name: str
    name: str


class Job(NamedTuple):
    name: str


# TODO type annotation: list vs List vs Sequence / others?
class UpsolverApi(metaclass=ABCMeta):
    @abstractmethod
    def authenticate(self, username: str, password: str) -> ProfileAuthSettings:
        pass

    @abstractmethod
    def get_completions(self, doc: Document) -> list[Completion]:
        pass

    @abstractmethod
    def lex_document(self, doc: Document) -> Callable[[int], StyleAndTextTuples]:
        pass

    @abstractmethod
    def check_syntax(self, expression: str) -> list[str]:
        pass

    @abstractmethod
    def execute(self, expression: str) -> list[dict[Any, Any]]:
        """
        :return: list of dictionary objects (keys are column names, values are column values),
                 each representing a result value.
        """
        pass

    @abstractmethod
    def get_clusters(self) -> list[Cluster]:
        pass

    @abstractmethod
    def export_cluster(self, cluster: str) -> str:
        pass

    @abstractmethod
    def stop_cluster(self, cluster: str) -> Optional[str]:
        pass

    @abstractmethod
    def run_cluster(self, cluster: str) -> Optional[str]:
        pass

    @abstractmethod
    def delete_cluster(self, cluster: str) -> Optional[str]:
        pass

    @abstractmethod
    def get_catalogs(self) -> list[Catalog]:
        pass

    @abstractmethod
    def export_catalog(self, catalog: str) -> str:
        pass

    @abstractmethod
    def get_tables(self) -> list[Table]:
        pass

    @abstractmethod
    def export_table(self, table: str) -> str:
        pass

    @abstractmethod
    def get_table_partitions(self, table: str) -> list[TablePartition]:
        pass

    @abstractmethod
    def get_jobs(self) -> list[Job]:
        pass

    @abstractmethod
    def export_job(self, job: str) -> str:
        pass


class UpsolverRestApi(UpsolverApi):
    # annotation of __init__ return type: https://www.python.org/dev/peps/pep-0484/:
    # (Note that the return type of __init__ ought to be annotated with -> None. The reason for this is
    # subtle. If __init__ assumed a return annotation of -> None, would that mean that an argument-less,
    # un-annotated __init__ method should still be type-checked? Rather than leaving this ambiguous or
    # introducing an exception to the exception, we simply say that __init__ ought to have a return
    # annotation; t~he default behavior is thus the same as for other methods.)
    def __init__(self,
                 auth_base_url: str,
                 auth_settings: Optional[ProfileAuthSettings]) -> None:
        self.auth_base_url = auth_base_url
        self.auth_settings = auth_settings

    def _base_url(self) -> str:
        if self.auth_settings is None:
            raise BadConfig('Missing auth settings')
        return self.auth_settings.base_url

    def _auth_token(self) -> str:
        if self.auth_settings is None:
            raise BadConfig('Missing auth settings')
        return self.auth_settings.token

    def _gen_api_token(self, username: str, password: str) -> str:
        try:
            with requests.post(
                    url=f'http://{self.auth_base_url}/api-tokens/',
                    headers={
                        'X-Api-Email': username,
                        'X-Api-Password': password,
                    },
                    json={
                        'displayData': {
                            'name': f'apitoken-{username}-{datetime.datetime.now().timestamp()}',
                            'description': 'CLI generated token'
                        }
                    }
            ) as resp:
                return resp.json()['apiToken']
        except Exception as ex:
            raise ApiErr(ex)

    def _get_base_url(self, token: str) -> str:
        try:
            with requests.get(
                    url=f'http://{self.auth_base_url}/environments/local-api/',
                    headers={'Authorization': token},
            ) as resp:
                return resp.json()['dnsInfo']['name']
        except Exception as ex:
            raise ApiErr(ex)

    def authenticate(self, username: str, password: str) -> ProfileAuthSettings:
        api_token = self._gen_api_token(username, password)
        base_url = self._get_base_url(api_token)

        self.auth_settings = ProfileAuthSettings(token=api_token, base_url=base_url)
        return self.auth_settings

    # TODO serializing Document
    # TODO what is the upsolver API for completion
    # TODO limitation of using API here: we get a complete list of all candidates
    #      (unless we want to use paging? sort of overkill...)
    def get_completions(self, doc: Document) -> list[Completion]:
        return list()

    def lex_document(self, doc: Document) -> Callable[[int], StyleAndTextTuples]:
        def emptylist(i: int) -> StyleAndTextTuples:
            return list()

        return emptylist

    # TODO does it make sense to have this API call?
    #      alternative is to have a lexer/parser running locally
    # TODO meaning of Sequence == immutable, iterable collection of items?
    def check_syntax(self, expression: str) -> list[str]:
        """
        :param expression: expression to check the syntax of
        :return: a sequence of error messages. If there are no errors in the syntax of `expression` an empty
                 sequence should be returned.
        """
        if "this is bad" in expression:
            return list("err:12:bad")
        else:
            return list()

    def execute(self, expression: str) -> list[dict[Any, Any]]:
        # if we allow expression to contain multiple statements (separated by ;) then the
        # responses will have to be handled accordingly: the response body is a list where
        # each entry refers to the execution status of corresponding expression...
        # for now it's easier to assume that expression is a singular statement to be executed
        expression = expression.split(';')[0]  # TODO allow execution of multiple statements?

        initial_resp = requests.post(
            url=f'http://{self._base_url()}/query/',
            headers={'Authorization': self._auth_token()},
            json={
                'sql': expression,
                'range': {
                    'start': {'line': 1, 'column': 1},
                    'end': {'line': 1, 'column': 1},
                },
            },
        )

        def drain(resp: Response) -> list[dict[Any, Any]]:
            def raise_err() -> None:
                raise ApiErr(f'Failed to execute "{expression}": '
                             f'status_code={resp.status_code}, '
                             f'payload={resp.json()}')

            try:
                tmp = resp.json()
                # TODO multiple statements within 'expression'
                #   reason for list or dict: response to initial requst (post) is a list, the
                #   other responses (to get requests that use url suffix provided by previous
                #   responses) are dicts.
                rjson = tmp[0] if type(tmp) is list else tmp
            except Exception as ex:
                raise ApiErr(ex)

            sc = resp.status_code
            if int(sc / 100) != 2:
                raise_err()

            status = rjson['status']
            is_success = sc == 200 and status == 'Success'

            # 201 is CREATED; returned on initial creation of "pending" response
            # 202 is ACCEPTED; returned if existing pending query is still not ready
            is_pending = (sc == 201 or sc == 202) and status == 'Pending'
            if not(is_success or is_pending):
                raise_err()

            if is_pending:
                max_wait_time_secs = 10.0  # TODO make configurable
                waited_secs = 0.0
                while waited_secs < max_wait_time_secs:
                    to_wait_secs = 0.5
                    time.sleep(to_wait_secs)
                    waited_secs += to_wait_secs
                    return drain(requests.get(
                        url=f'http://{self._base_url()}{rjson["current"]}',
                        headers={'Authorization': self._auth_token()},
                    ))

                raise ApiErr('Timeout.')

            result = rjson['result']
            grid = result['grid']  # columns, data, ...
            column_names = [c['name'] for c in grid['columns']]
            data_w_columns = [dict(zip(column_names, row)) for row in grid['data']]
            next = result.get('next')
            return data_w_columns + (
                [] if next is None
                else drain(requests.get(
                    url=f'http://{self._base_url()}{next}',
                    headers={'Authorization': self._auth_token()},
                ))
            )

        return drain(initial_resp)

    def _http_get(self, url_suffix: str) -> dict[Any, Any]:
        try:
            with requests.get(
                url=f'http://{self._base_url()}/{url_suffix}',
                headers={'Authorization': self._auth_token()}
            ) as resp:
                return resp.json()
        except Exception as ex:
            raise ApiErr(ex)

    def get_clusters(self) -> list[Cluster]:
        environments = [
            dashboard_ele['environment']
            for dashboard_ele in self._http_get('environments/dashboard')
        ]

        return [
            Cluster(name=env['displayData']['name'], id=env['id'])
            for env in environments
        ]

    def export_cluster(self, cluster: str) -> str:
        return f'CREATE CLUSTER {cluster}'

    def stop_cluster(self, cluster: str) -> Optional[str]:
        """
        :return: A string detailing an error, or None if there were no errors
        """
        return None

    def run_cluster(self, cluster: str) -> Optional[str]:
        """
        :return: A string detailing an error, or None if there were no errors
        """
        return None

    def delete_cluster(self, cluster: str) -> Optional[str]:
        """
        :return: A string detailing an error, or None if there were no errors
        """
        return None

    def get_catalogs(self) -> list[Catalog]:
        return [
            Catalog(
                id=c['id'],
                name=c['connection']['displayData']['name'],
                created_by=c['connection']['displayData'].get('createdBy'),
                kind=c['connection']['clazz'],
                orgId=c['organizationId'],
            )
            for c in self._http_get('connections')
        ]

    def export_catalog(self, catalog: str) -> str:
        return f'CREATE CONNECTION {catalog}'

    def get_tables(self) -> list[Table]:
        return [Table(name='stamtable')]

    def export_table(self, table: str) -> str:
        return f'CREATE TABLE {table}'

    def get_table_partitions(self, table: str) -> list[TablePartition]:
        return [TablePartition(table_name=table, name='stampartition')]

    def get_jobs(self) -> list[Job]:
        return [Job(name='stamjob')]

    def export_job(self, job: str) -> str:
        return f'CREATE JOB {job}'


class UpsolverApiCompleter(Completer):
    def __init__(self, api: UpsolverApi):
        self.api = api

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        # TODO what is complete_event for?
        return self.api.get_completions(document)


class FooCompleter(Completer):
    def __init__(self, api: UpsolverApi):
        self.api = api

    _meta_commands: dict[str, str] = {
        '!exit': 'Exit from the interactive UpSQL shell',
        '!quit': 'Quit the interactive UpSQL shell',
        '!help': 'Show Help',
    }

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        return [
            Completion(
                text=match,
                display_meta=self._meta_commands[match],
                start_position=-len(document.text)  # TODO wtf
            )
            for match in [k for k in self._meta_commands.keys() if k.startswith(document.text)]
        ]


class UpsolverApiLexer(Lexer):
    def __init__(self, api: UpsolverApi):
        self.api = api

    # returns: a callable that takes a **line number**
    #          and returns a list of ``(style_str, text)`` tuples for that line
    # TODO not sure how the API will return this? How does this even work?
    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        return self.api.lex_document(document)
