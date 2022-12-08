from typing import Optional

import click

from cli.commands.context import CliContext
from cli.config import Profile
from cli.errors import ConfigErr
from cli.formatters import OutputFmt, get_output_format
from cli.utils import parse_url


@click.command(help='Interactively configure CLI settings')
@click.pass_obj
@click.option('-t', '--token', default=None,
              help='Token to use.')
@click.option('-u', '--api-url', default=None,
              help='URL of Upsolver\'s API.')
@click.option('-o', '--output-format', default=None,
              help='The format that the results will be returned in. '
                   'Supported formats: Json, Csv, Tsv, Plain. Default is Json.')
def configure(ctx: CliContext,
              token: Optional[str],
              api_url: Optional[str],
              output_format: Optional[str]) -> None:
    profile = ctx.confman.conf.active_profile

    token = token or profile.token
    if token is None:
        raise ConfigErr("Can't create a new profile without a token, pleas provide it by using -t flag.")

    base_url = parse_url(api_url) if api_url else profile.base_url
    if base_url is None:
        raise ConfigErr("Can't create a new profile without a api-url, pleas provide it by using -u flag.")
    assert base_url.is_absolute()

    output = get_output_format(output_format) or profile.output or OutputFmt.JSON

    ctx.confman.update_profile(
        Profile(
            name=profile.name,
            token=token,
            base_url=base_url,
            output=output
        )
    )
