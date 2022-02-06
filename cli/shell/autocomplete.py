# TODO(CR) change name / move ; create separate dir for these (completers, lexers)
from typing import Iterable

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document

from cli.upsolver.lsp import LspApi


class LspCompleter(Completer):
    def __init__(self, lsp: LspApi):
        self.lsp = lsp

    _meta_commands: dict[str, str] = {
        '!exit': 'Exit from the interactive UpSQL shell',
        '!quit': 'Quit the interactive UpSQL shell',
        '!help': 'Show Help',
    }

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        return self.lsp.get_completions(document)
