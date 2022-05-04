import dataclasses

import click

from cli.commands.context import CliContext
from cli.ui import stats_screen
from cli.upsolver import entities


@click.group()
def tables() -> None:
    """
    View & manage tables
    """
    pass


@tables.command(help='List clusters')
@click.pass_obj
def ls(ctx: CliContext) -> None:
    ctx.write(ctx.upsolver_api().get_tables_raw())


@tables.command(help='Display a live stream of table(s) statistics')
@click.pass_obj
@click.argument('tables', nargs=-1)
def stats(ctx: CliContext, tables: list[str]) -> None:
    api = ctx.upsolver_api()
    stats_screen(
        title='Table Stats',
        headers=[f.name for f in dataclasses.fields(entities.Table)],
        get_values=lambda: [
            t for t in api.get_tables()
            if (len(tables) == 0) or (t.name in tables)
        ]
    )


@tables.command(help='Export a certain table as a "CREATE TABLE" sql command that can be '
                     'used in an "upsolver execute" command')
@click.pass_obj
@click.argument('table', nargs=1)
def export(ctx: CliContext, table: str) -> None:
    ctx.echo(ctx.upsolver_api().export_table(table))


@tables.command(help='Display the partitions of a given table')
@click.pass_obj
@click.argument('table', nargs=1)
def partitions(ctx: CliContext, table: str) -> None:
    ctx.write(ctx.upsolver_api().get_table_partitions(table))
