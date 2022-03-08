from typing import Optional

import click

from cli.commands.context import CliContext
from cli.upsolver.requester import parse_url


@click.command(help='Login and retrieve API token')
@click.pass_obj
@click.option('-u', '--base-url', default=None,
              help='URL of Upsolver\'s Authentication API (default is https://api.upsolver.com)')
def login(ctx: CliContext, base_url: Optional[str]) -> None:
    # get login info from user
    email = click.prompt('Email')
    password = click.prompt('Password', hide_input=True)

    # auth against api
    api = ctx.auth_api(parse_url(base_url))
    profile_auth_settings = api.authenticate(email, password)

    # update profile in configuration
    updated_profile = profile_auth_settings.update(ctx.confman.conf.active_profile)
    ctx.confman.update_profile(updated_profile)

    ctx.echo(
        f'Successfully configured profile \'{updated_profile.name}\' '
        f'(API access token: {updated_profile.token})'
    )
