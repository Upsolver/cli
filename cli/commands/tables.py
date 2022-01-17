import click
from click import echo

from cli.commands.context import CliContext


@click.group()
def tables() -> None:
    """
    View & manage tables
    """
    pass


@tables.command(help='List clusters')
@click.pass_obj
def ls(ctx: CliContext) -> None:
    echo('\n'.join([c.name for c in ctx.upsolver_api().get_tables()]))


@tables.command(help='Display a live stream of table(s) statistics')
@click.argument('tables', nargs=-1)
def stats(tables: list[str]) -> None:
    echo(f'running tables stats (tables=[{", ".join(tables)}]) ... ')


@tables.command(help='Export a certain table as a "CREATE TABLEW" sql command that can be '
                     'used in an "upsolver execute" command')
@click.pass_obj
@click.argument('table', nargs=1)
def export(ctx: CliContext, table: str) -> None:
    echo(ctx.upsolver_api().export_table(table))


@tables.command(help='Display the partitions of a given table')
@click.pass_obj
@click.argument('table', nargs=1)
def partitions(ctx: CliContext, table: str) -> None:
    echo(ctx.upsolver_api().get_table_partitions(table))
