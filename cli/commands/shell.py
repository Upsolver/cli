import click

from cli.commands.context import CliContext
from cli.shell.shell import UpsolverShell


@click.command()
@click.pass_obj
def shell(ctx: CliContext) -> None:
    """
    An interactive SQL shell
    """
    UpsolverShell(ctx.upsolver_api(), ctx.confman.get_formatter()).repl()
