from abc import ABCMeta, abstractmethod


class QueryLexer(metaclass=ABCMeta):
    """
    Lexer for the upsolver SQL-dialect.

    TODO combine this w/ the lexer required by prompt toolkit?
    TODO use ANTLR lexer? expect support from API for execution of multiple queries?
    """

    @abstractmethod
    def split(self, queries: str) -> list[str]:
        """
        splits a string that can potentially contain multiple queries into a list of
        individual queries.
        """
        pass


class SimpleQueryLexer(QueryLexer):
    def split(self, queries: str) -> list[str]:
        return [q for q in queries.split(';') if len(q) > 0]
