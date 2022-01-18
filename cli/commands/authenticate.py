from typing import Optional

import click

from cli.commands.context import CliContext
from cli.config import parse_url


@click.command(help='Retrieve API token to perform further actions')
@click.pass_obj
# TODO @click.option('-t', '--token', default=None, help='Authentication token')
@click.option('-e', '--email', required=True, help='User\'s email')
@click.option('-p', '--password', required=True, help='User\'s Password')
@click.option('-u', '--base-url', default=None,
              help='URL of Upsolver\'s Authentication API '
                   '(for example: "-u https://api.upsolver.com")"')
def authenticate(ctx: CliContext, email: str, password: str, base_url: Optional[str]) -> None:
    api = ctx.upsolver_api(parse_url(base_url))
    profile_auth_settings = api.authenticate(email, password)
    updated_profile = profile_auth_settings.update(ctx.confman.conf.active_profile)
    ctx.confman.update_profile(updated_profile)
    ctx.echo(
        f'Successfully performed authentication for profile \'{updated_profile.name}\' '
        f'(auth token: {updated_profile.token}, base url: {updated_profile.base_url})'
    )
