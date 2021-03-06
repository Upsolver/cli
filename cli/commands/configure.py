import click
from yarl import URL

from cli.commands.context import CliContext
from cli.config import ConfigurationManager, Profile
from cli.formatters import OutputFmt


@click.command(help='Interactively configure CLI settings')
@click.pass_obj
def configure(ctx: CliContext) -> None:
    profile = ctx.confman.conf.active_profile
    ctx.confman.update_profile(Profile(
        name=profile.name,
        token=click.prompt('API Access Token', profile.token),
        base_url=URL(click.prompt('API Endpoint',
                                  profile.base_url if profile.base_url is not None
                                  else ConfigurationManager.CLI_DEFAULT_BASE_URL)),
        output=OutputFmt(click.prompt('Default Output Format', profile.output.value))
    ))
