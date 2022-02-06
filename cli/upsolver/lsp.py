from abc import ABCMeta, abstractmethod
from typing import Callable

from prompt_toolkit.completion import Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.sql import SqlLexer

from cli.upsolver.requester import Requester


class LspApi(metaclass=ABCMeta):
    """
    Support for these methods is expected from the upsolver API via the LSP protocol.
    """
    @abstractmethod
    def get_completions(self, doc: Document) -> list[Completion]:
        pass

    @abstractmethod
    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        pass


class RestLspApi(LspApi):
    def __init__(self, requester: Requester):
        self.requester = requester

    def get_completions(self, doc: Document) -> list[Completion]:
        return []

    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        pass


# TODO
class FakeLspApi(LspApi):
    _meta_commands: dict[str, str] = {
        '!exit': 'Exit from the interactive UpSQL shell',
        '!quit': 'Quit the interactive UpSQL shell',
        '!help': 'Show Help',
    }

    def __init__(self) -> None:
        self.pyg_lexer = PygmentsLexer(SqlLexer)

    def get_completions(self, doc: Document) -> list[Completion]:
        return [
            Completion(
                text=match,
                display_meta=self._meta_commands[match],
                start_position=-len(doc.text)  # TODO wtf
            )
            for match in [k for k in self._meta_commands.keys() if k.startswith(doc.text)]
        ]

    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        return self.pyg_lexer.lex_document(document)
