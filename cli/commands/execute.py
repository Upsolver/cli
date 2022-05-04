from pathlib import Path
from typing import Optional

import click
from click import echo

from cli.commands.context import CliContext
from cli.formatters import Formatter, OutputFmt
from cli.utils import convert_time_str


@click.command()
@click.pass_obj
@click.argument('expression')
@click.option('-o', '--output-format', default=None,
              help='The format that the results will be returned in')
@click.option('-t', '--timeout', 'timeout_sec', default='10s', callback=convert_time_str,
              help='Timeout setting for pending responses')
@click.option('-d', '--dry-run', is_flag=True, default=False,
              help='Validate expression is syntactically valid but don\'t run the command.')
@click.option('-s', '--ignore-errors', is_flag=True, default=False,
              help='Ignore errors in query responses. Default behavior is to stop on error.')
def execute(
    ctx: CliContext,
    expression: str,
    output_format: Optional[str],
    timeout_sec: float,
    dry_run: bool,
    ignore_errors: bool
) -> None:
    """
    Execute a single SQL query
    """
    expression = expression.strip()

    if expression == '-':
        expression = click.get_text_stream('stdin').read().strip()
    else:
        p = Path(expression)
        if p.exists():
            expression = p.read_text()

    if len(expression) == 0:
        return

    fmt: Optional[Formatter] = None
    if output_format is not None:
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
        queries = ctx.query_lexer().split(expression)
        for q in queries:
            if len(queries) > 1:
                ctx.write({'marker': 'execution_start', 'query': q})

            try:
                for res in api.execute(q, timeout_sec):
                    for res_part in res:
                        ctx.write(res_part, fmt)
            except Exception as ex:
                if not ignore_errors:
                    raise ex
                else:
                    if len(queries) > 1:
                        ctx.write({'query': q, 'error': str(ex)})
                    else:
                        click.echo(str(ex))
