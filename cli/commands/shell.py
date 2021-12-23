import click

from cli.commands.context import CliContext
from cli.shell.shell import UpsolverShell


@click.command()
@click.pass_context
def shell(ctx: click.Context) -> None:
    clictx = ctx.ensure_object(CliContext)
    UpsolverShell(clictx.upsolver_api()).repl()
