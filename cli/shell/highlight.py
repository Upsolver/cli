from typing import Callable

from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.lexers import Lexer

from cli.upsolver.lsp import LspApi


class LspLexer(Lexer):
    def __init__(self, lsp: LspApi):
        self.lsp = lsp

    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        return self.lsp.lex_document(document)
