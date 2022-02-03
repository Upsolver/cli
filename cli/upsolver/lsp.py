from abc import ABCMeta, abstractmethod
from typing import Callable

from prompt_toolkit.completion import Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import StyleAndTextTuples

from cli.upsolver.requester import Requester


class LspApi(metaclass=ABCMeta):
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
