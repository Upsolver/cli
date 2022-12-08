from pathlib import Path
from typing import Optional

import click
from click import echo

from cli.commands.context import CliContext
from cli.config import ProfileAuthSettings
from cli.errors import ConfigErr
from cli.formatters import Formatter, get_output_format
from cli.utils import convert_time_str, parse_url


@click.command()
@click.pass_obj
@click.argument('expression')
@click.option('-t', '--token', default=None,
              help='Token to use. Requires to provide api-url as well.')
@click.option('-u', '--api-url', default=None,
              help='URL of Upsolver\'s API. Requires to provide token as well.')
@click.option('-c', '--command', is_flag=True, default=False,
              help='Execute a string sql statement.')
@click.option('-o', '--output-format', default=None,
              help='The format that the results will be returned in. '
                   'Supported formats: Json, Csv, Tsv, Plain. Default is Json.')
@click.option('--timeout', 'timeout_sec', default='10s', callback=convert_time_str,
              help='Timeout setting for pending responses.')
@click.option('-d', '--dry-run', is_flag=True, default=False,
              help='Validate expression is syntactically valid but don\'t run the command.')
@click.option('-s', '--ignore-errors', is_flag=True, default=False,
              help='Ignore errors in query responses. Default behavior is to stop on error.')
def execute(
        ctx: CliContext,
        expression: str,
        token: Optional[str],
        api_url: Optional[str],
        command: bool,
        output_format: Optional[str],
        timeout_sec: float,
        dry_run: bool,
        ignore_errors: bool,
) -> None:
    """
    Execute a single SQL query
    """
    expression = expression.strip()

    if expression == '-':
        expression = click.get_text_stream('stdin').read().strip()
    else:
        if not command:
            p = Path(expression)
            if p.exists():
                expression = p.read_text()
            else:
                raise ConfigErr("File not found in location: {}".format(expression))

    if len(expression) == 0:
        return

    output_format = get_output_format(output_format)
    fmt: Optional[Formatter] = output_format.get_formatter() if output_format else None

    if token and api_url:
        api_url = parse_url(api_url)
        assert api_url.is_absolute()
        api = ctx.upsolver_api(ProfileAuthSettings(token, api_url))
    elif token or api_url:
        raise ConfigErr("Please provide api-url with token or use the `configure` sub-command "
                        "to create a proper profile and use it with -p flag.")
    else:
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
