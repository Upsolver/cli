from typing import Optional

import click

from cli.commands.context import CliContext
from cli.utils import parse_url


@click.command(help='Login and retrieve API token')
@click.pass_obj
@click.option('-e', '--email', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-u', '--base-url', default=None,
              help='URL of Upsolver\'s Authentication API (default is https://api.upsolver.com)')
def login(ctx: CliContext, email: str, password: str, base_url: Optional[str]) -> None:
    # perform authentication
    api = ctx.auth_api(parse_url(base_url))
    profile_auth_settings = api.authenticate(email, password)

    # update profile in configuration
    updated_profile = profile_auth_settings.update(ctx.confman.conf.active_profile)
    ctx.confman.update_profile(updated_profile)

    ctx.echo(
        f'Successfully configured profile \'{updated_profile.name}\' '
        f'(API access token: {updated_profile.token})'
    )
