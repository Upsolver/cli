from typing import Optional

import click
from click import echo

from cli.commands.context import CliContext
from cli.formatters import Formatter, OutputFmt


@click.command()
@click.pass_obj
@click.argument('expression')
@click.option('-o', '--output-format', default='json',
              help='The format that the results will be returned in')
@click.option('-d', '--dry-run', is_flag=True, default=False,
              help='Validate expression is syntactically valid but don\'t run the command.')
def execute(
    ctx: CliContext,
    expression: str,
    output_format: str,
    dry_run: bool,
) -> None:
    """
    Execute a single SQL query
    """
    expression = expression.strip()
    if expression == '-':
        expression = click.get_text_stream('stdin').read().strip()

    if len(expression) == 0:
        return

    fmt: Optional[Formatter] = None
    try:
        fmt = OutputFmt(output_format.lower()).get_formatter()
    except ValueError:
        pass

    api = ctx.upsolver_api()
    if dry_run:
        check_result = api.check_syntax(expression)
        if len(check_result) > 0:
            check_result_txt = "\n".join(check_result)
            echo(err=True, message=f'found following errors in expression:\n{check_result_txt})')
        else:
            echo("Expression is valid.")
    else:
        for q in ctx.query_lexer().split(expression):
            for res in api.execute(q):
                ctx.write(res, fmt)
