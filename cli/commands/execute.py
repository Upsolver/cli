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
@click.option('-f', '--file_path', default=None,
              help='Execute a file.')
@click.option('-c', '--command', default=None,
              help='Execute a string sql statement.')
@click.option('-t', '--token', default=None,
              help='Token to use. Requires to provide api-url as well.')
@click.option('-u', '--api-url', default=None,
              help='URL of Upsolver\'s API. Requires to provide token as well.')
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
        file_path: Optional[str],
        command: Optional[str],
        token: Optional[str],
        api_url: Optional[str],
        output_format: Optional[str],
        timeout_sec: float,
        dry_run: bool,
        ignore_errors: bool
) -> None:
    """
    Execute a single SQL query, using -f <file_path> or -c <sql_command>
    """
    expression = __get_expression(file_path, command)

    output_format = get_output_format(output_format)
    fmt: Optional[Formatter] = output_format.get_formatter() if output_format else None

    if token and api_url:
        api_url = parse_url(api_url)
        api = ctx.upsolver_api(ProfileAuthSettings(token, api_url))
    elif token or api_url:
        raise ConfigErr("Please provide a token and an api-url.")
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
        try:
            for res in api.execute(expression, timeout_sec):
                for res_part in res:
                    ctx.write(res_part, fmt)
        except Exception as ex:
            if not ignore_errors:
                raise ex
            else:
                click.echo(str(ex))


def __get_expression(file_path: Optional[str], command: Optional[str]) -> str:
    if (file_path and command) or (not file_path and not command):
        raise ConfigErr("Please provide either a file path (using -f flag) "
                        "or a sql statement (using -c flag).")
    if file_path:
        p = Path(file_path)
        if p.exists():
            return p.read_text()
        else:
            raise ConfigErr("File not found in location: {}".format(file_path))
    if command:
        return command.strip()
