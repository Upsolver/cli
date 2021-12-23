import click

from cli.commands.context import CliContext


@click.command(help='Perform Authentication and save auth token in config file')
@click.pass_context
@click.option('-t', '--token', required=True, help='Authentication token')
def authenticate(ctx: click.Context, token: str) -> None:
    clictx = ctx.ensure_object(CliContext)
    profile_auth_settings = clictx.authenticator()(token)
    updated_profile = profile_auth_settings.update(clictx.conf.active_profile)
    clictx.update_profile_conf(updated_profile)
