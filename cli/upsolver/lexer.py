from abc import ABCMeta, abstractmethod

import sqlparse


class QueryLexer(metaclass=ABCMeta):
    """
    Lexer for the upsolver SQL-dialect.
    """

    @abstractmethod
    def split(self, queries: str) -> list:
        """
        splits a string that can potentially contain multiple queries into a list of
        individual queries.
        """
        pass


class SimpleQueryLexer(QueryLexer):
    def split(self, queries: str) -> list:
        return [s for s in [s.strip() for s in sqlparse.split(queries)] if s != ';']
