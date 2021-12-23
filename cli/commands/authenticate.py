import click
from click import echo

from cli.commands.context import CliContext

"""
# TODO
        --token        Authenticate to Upsolver via an Authentication token
        --browser      Authenticate to Upsolver via a browser
"""


@click.command()
@click.pass_context
@click.option('-t', '--token', required=True, help='Authentication token')
def authenticate(
    ctx: click.Context,
    token: str
) -> None:
    clictx = ctx.find_object(CliContext)
    # TODO need confparser here so I can write to config file...
    clictx.conf.active_profile
    echo('Authenticated.')
