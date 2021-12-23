from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import ThreadedCompleter
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import HasFocus, IsDone
from prompt_toolkit.layout.processors import (
    ConditionalProcessor,
    HighlightMatchingBracketProcessor,
    TabsProcessor,
)
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.sql import SqlLexer

from cli.upsolver import UpsolverApi, UpsolverApiCompleter


class UpsolverShell(object):
    # TODO need to pass the configuration options from ~/.upsql/config here (?)
    def __init__(self, api: UpsolverApi):
        self.api = api

    def run_cli(self) -> None:
        session: PromptSession[str] = PromptSession(
            'upsql> ',
            history=None,
            auto_suggest=AutoSuggestFromHistory(),

            # TODO upsolver lexer causes exception in event loop
            # lexer=UpsolverApiLexer(self.api),  # PygmentsLexer(SqlLexer),  # used for syntax highlighting

            lexer=PygmentsLexer(SqlLexer),
            enable_history_search=False,
            # TODO not sure ? indicate when up-arrow partial string matching is enabled. It is advised
            #  to not enable this at the same time as complete_while_typing, because when there is
            #  an autocompletion found, the up arrows usually browse through the completions,
            #  rather than through the history.
            completer=ThreadedCompleter(UpsolverApiCompleter(self.api)),
            multiline=False,  # TODO figure out how to get return from prompt() if I set this to True

            # TODO (taken from pgcli) haven't tested input_processors
            input_processors=[
                # Highlight matching brackets while editing.
                ConditionalProcessor(
                    processor=HighlightMatchingBracketProcessor(chars="[](){}"),
                    filter=HasFocus(DEFAULT_BUFFER) & ~IsDone(),
                ),
                # Render \t as 4 spaces instead of "^I"
                TabsProcessor(char1=" ", char2=" "),
            ],
        )

        while True:
            text = session.prompt()
            print(f'executing command ...{text}')
            if text == 'quit' or text == 'exit':
                return
