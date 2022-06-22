import click

from cli.commands.context import CliContext
from cli.utils import find_by_name_or_id


@click.group()
def catalogs() -> None:
    """
    View & manage catalogs (connections)
    """
    pass


@catalogs.command(help='List all catalogs')
@click.pass_obj
def ls(ctx: CliContext) -> None:
    ctx.write(ctx.upsolver_api().catalogs.raw.get())


@catalogs.command(help='Export a catalog (connection) as a "CREATE CONNECTION" sql command')
@click.pass_obj
@click.argument('catalog', nargs=1)
def export(ctx: CliContext, catalog: str) -> None:
    catalogs_api = ctx.upsolver_api().catalogs
    ctx.write(
        catalogs_api.export(
            find_by_name_or_id(catalog, catalogs_api.get()).id
        )
    )
