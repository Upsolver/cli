import click
from click import echo


@click.group()
def catalogs() -> None:
    pass


@catalogs.command(help='List the catalogs')
def ls() -> None:
    echo("listing catalogs ...")


@catalogs.command(help='Export a certain catalog as a "CREATE CONNECTION" sql command')
@click.argument('catalog', nargs=1)
def export(catalog: str) -> None:
    echo(f'exporting "{catalog}" catalog...')
