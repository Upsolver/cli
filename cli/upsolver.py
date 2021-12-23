from typing import Callable, Iterable, Sequence

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.lexers import Lexer

# TODO abstract class, implementations: actual, mock (tests, mocking lib for python?), local


class UpsolverApi(object):
    # annotation of __init__ return type: https://www.python.org/dev/peps/pep-0484/:
    # (Note that the return type of __init__ ought to be annotated with -> None. The reason for this is
    # subtle. If __init__ assumed a return annotation of -> None, would that mean that an argument-less,
    # un-annotated __init__ method should still be type-checked? Rather than leaving this ambiguous or
    # introducing an exception to the exception, we simply say that __init__ ought to have a return
    # annotation; the default behavior is thus the same as for other methods.)
    def __init__(self) -> None:
        pass

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
    def check_syntax(self, expression: str) -> Sequence[str]:
        """
        :param expression: expression to check the syntax of
        :return: a sequence of error messages. If there are no errors in the syntax of `expression` an empty
                 sequence should be returned.
        """
        if "this is bad" in expression:
            return list("err:12:bad")
        else:
            return list()

    # TODO two types of responses: simple, streaming
    #      what would the simple response look like? (it's a json string...)
    #      streaming is a sequence of simples (perhaps additional positional information +
    #      "get next" identifier)?
    def execute(self, expression: str) -> str:
        return '<no result>'


class UpsolverApiCompleter(Completer):
    def __init__(self, api: UpsolverApi):
        self.api = api

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        # TODO what is complete_event for?
        return self.api.get_completions(document)


class UpsolverApiLexer(Lexer):
    def __init__(self, api: UpsolverApi):
        self.api = api

    # returns: a callable that takes a **line number**
    #          and returns a list of ``(style_str, text)`` tuples for that line
    # TODO not sure how the API will return this? How does this even work?
    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        return self.api.lex_document(document)
