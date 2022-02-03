from abc import ABC
from typing import Callable, Iterable

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.lexers import Lexer

# TODO type annotation: list vs List vs Sequence / others?
from cli.upsolver.auth import AuthApi
from cli.upsolver.catalogs import CatalogsApi
from cli.upsolver.clusters import ClustersApi
from cli.upsolver.jobs import JobsApi
from cli.upsolver.lsp import LspApi
from cli.upsolver.query import QueryApi
from cli.upsolver.tables import TablesApi

# TODO
#   - [ ] abstract class, implementations: actual, mock (tests, mocking lib for python?), local
#   - [ ] retries? timeouts?


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


class UpsolverApiCompleter(Completer):
    def __init__(self, api: UpsolverApi):
        self.api = api

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        # TODO purpose of complete_event?
        return self.api.get_completions(document)


# TODO(CR) change name / move ; create separate dir for these (completers, lexers)
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
