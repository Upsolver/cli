import click

from cli.commands.context import CliContext


@click.group()
def catalogs() -> None:
    """
    View & manage catalogs (connections)
    """
    pass


@catalogs.command(help='List all catalogs')
@click.pass_obj
def ls(ctx: CliContext) -> None:
    ctx.write(ctx.upsolver_api().get_catalogs())


@catalogs.command(help='Export a certain catalog as a "CREATE CONNECTION" sql command')
@click.pass_obj
@click.argument('catalog', nargs=1)
def export(ctx: CliContext, catalog: str) -> None:
    ctx.echo(ctx.upsolver_api().export_catalog(catalog))
