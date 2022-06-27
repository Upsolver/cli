import click

from cli.commands.context import CliContext


@click.group()
def worksheets() -> None:
    """
    View & manage Worksheets
    """
    pass


@worksheets.command(help='List worksheets')
@click.pass_obj
def ls(ctx: CliContext) -> None:
    ctx.write(ctx.upsolver_api().worksheets.list())
