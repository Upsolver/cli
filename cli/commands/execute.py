from pathlib import Path
from typing import Optional

import click

from cli.commands.context import CliContext
from cli.errors import ApiUnavailable, ConfigErr
from cli.formatters import Formatter, get_output_format
from cli.upsolver.api_utils import get_base_url
from cli.upsolver.auth_filler import TokenAuthFiller
from cli.upsolver.poller import SimpleResponsePoller
from cli.upsolver.query import RestQueryApi
from cli.upsolver.requester import Requester
from cli.utils import convert_time_str, get_logger


@click.command(help='Execute a single SQL query. '
                    'Use -f <file_path> or -c <sql_command>.', no_args_is_help=True)
@click.pass_obj
@click.option('-f', '--file_path', default=None,
              help='Execute a file.')
@click.option('-c', '--command', default=None,
              help='Execute a string sql statement.')
@click.option('-t', '--token', default=None,
              help='Token to use.')
@click.option('-u', '--api-url', default=None,
              help='URL of Upsolver\'s API. If not provided, we will try to get it automatically from the '
                   'authentication API.')
@click.option('-o', '--output-format', default=None,
              help='The format that the results will be returned in. '
                   'Supported formats: Json, Csv, Tsv, Plain. Default is Json.')
@click.option('--timeout', 'timeout_sec', default='30s', callback=convert_time_str,
              help='Timeout setting for pending responses. Default is 30s.')
def execute(
        ctx: CliContext,
        file_path: Optional[str],
        command: Optional[str],
        token: Optional[str],
        api_url: Optional[str],
        output_format: Optional[str],
        timeout_sec: float) -> None:
    logger = get_logger('execute')

    expression = __get_expression(file_path, command)

    output_format = get_output_format(output_format)
    fmt: Optional[Formatter] = output_format.get_formatter() if output_format else None

    auth_api_url = ctx.confman.auth_api_url
    logger.debug(f"Authentication API URL: {auth_api_url}")

    token = token or ctx.confman.conf.active_profile.token
    if token is None:
        raise ConfigErr("Please provide a token.")
    logger.debug(f"Token: {token}")

    api_url = api_url or ctx.confman.conf.active_profile.base_url or get_base_url(auth_api_url, token)
    if api_url is None:
        raise ApiUnavailable(auth_api_url)
    logger.debug(f"API URL: {api_url}")

    upsolver_api = RestQueryApi(
        requester=Requester(
            base_url=api_url,
            auth_filler=TokenAuthFiller(token)
        ),
        poller_builder=lambda to_sec: SimpleResponsePoller(max_time_sec=to_sec)
    )

    for res in upsolver_api.execute(expression, timeout_sec):
        for res_part in res:
            ctx.write(res_part, fmt)


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
