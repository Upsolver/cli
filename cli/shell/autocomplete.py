from typing import Iterable

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document

from cli.upsolver.lsp import LspApi


class LspCompleter(Completer):
    def __init__(self, lsp: LspApi):
        self.lsp = lsp

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        return self.lsp.get_completions(document)
