from typing import Optional

import click

from cli.commands.context import CliContext
from cli.upsolver.requester import parse_url


@click.command(help='Interactively configure CLI settings')
@click.pass_obj
# TODO @click.option('-t', '--token', default=None, help='Authentication token')
@click.option('-e', '--email', prompt=True, help='User\'s email')
@click.option('-p', '--password', prompt=True, hide_input=True, help='User\'s Password')
@click.option('-u', '--base-url', default=None,
              help='URL of Upsolver\'s Authentication API '
                   '(for example: "-u https://api.upsolver.com")"')
def configure(ctx: CliContext, email: str, password: str, base_url: Optional[str]) -> None:
    api = ctx.auth_api(parse_url(base_url))
    profile_auth_settings = api.authenticate(email, password)
    updated_profile = profile_auth_settings.update(ctx.confman.conf.active_profile)
    ctx.confman.update_profile(updated_profile)
    ctx.echo(
        f'Successfully configured profile \'{updated_profile.name}\' '
        f'(auth token: {updated_profile.token})'
    )
