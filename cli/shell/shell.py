import sys

from click import echo
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

from cli.config import Formatter
from cli.shell.autocomplete import LspCompleter
from cli.shell.highlight import LspLexer
from cli.upsolver.api import UpsolverApi


class UpsolverShell(object):
    def __init__(self, api: UpsolverApi, formatter: Formatter) -> None:
        self.api = api
        self.formatter = formatter

    def repl(self) -> None:
        session: PromptSession[str] = PromptSession(
            'upsql> ',
            history=None,
            auto_suggest=AutoSuggestFromHistory(),
            lexer=LspLexer(self.api),
            enable_history_search=False,
            search_ignore_case=True,
            completer=ThreadedCompleter(LspCompleter(self.api)),
            multiline=False,
            input_processors=[
                ConditionalProcessor(  # Highlight matching brackets while editing.
                   processor=HighlightMatchingBracketProcessor(chars="[](){}"),
                   filter=HasFocus(DEFAULT_BUFFER) & ~IsDone(),
                ),
                TabsProcessor(char1=" ", char2=" "),  # Render \t as 4 spaces instead of "^I"
            ],
        )

        while True:
            text = session.prompt()
            if text in ['!quit', 'quit', '!exit', 'exit']:
                echo('Byeeeeeee')
                return
            elif text.startswith('!'):
                echo(f'Unknown command: {text}')
            else:
                try:
                    result = self.api.execute(text)
                    echo(message=self.formatter(result), file=sys.stdout)
                except Exception as ex:
                    echo(message=ex, file=sys.stderr)
