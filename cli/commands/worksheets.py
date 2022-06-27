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


@worksheets.command(help='Get worksheet')
@click.pass_obj
@click.argument('identifier', nargs=1)
def get(ctx: CliContext,
        identifier: str) -> None:
    ctx.write(ctx.upsolver_api().worksheets.get_worksheet(identifier))
