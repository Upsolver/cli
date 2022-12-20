from typing import Optional

import click

from cli.commands.context import CliContext
from cli.config import Profile
from cli.formatters import get_output_format
from cli.utils import parse_url


@click.command(help='Configure CLI settings. '
                    'In order to create a new profile you should provide a token and an api-url. '
                    'If you want to name the profile use the -p flag.', no_args_is_help=True)
@click.pass_obj
@click.option('-t', '--token', default=None,
              help='Token to use.')
@click.option('-u', '--api-url', default=None,
              help='URL of Upsolver\'s API. If not provided, we will try to get it automatically'
                   ' from the authentication API.')
@click.option('-o', '--output-format', default=None,
              help='The format that the results will be returned in. '
                   'Supported formats: Json, Csv, Tsv, Plain. Default is Json.')
@click.option('-f', '--force', is_flag=True, default=False,
              help='Overwrite profile if already exists.')
def configure(ctx: CliContext,
              token: Optional[str],
              api_url: Optional[str],
              output_format: Optional[str],
              force: bool) -> None:
    profile = ctx.confman.conf.active_profile

    base_url = parse_url(api_url) if api_url else None

    output = get_output_format(output_format) if output_format else None

    ctx.confman.update_profile(
        Profile(
            name=profile.name,
            token=token,
            base_url=base_url,
            output=output,
        ),
        force
    )
