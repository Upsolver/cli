import dataclasses

import click

from cli.commands.context import CliContext
from cli.ui import stats_screen
from cli.upsolver import entities
from cli.utils import find_by_name_or_id


@click.group()
def tables() -> None:
    """
    View & manage tables
    """
    pass


@tables.command(help='List clusters')
@click.pass_obj
def ls(ctx: CliContext) -> None:
    ctx.write(ctx.upsolver_api().tables.raw.list())


@tables.command(help='Display a live stream of table(s) statistics')
@click.pass_obj
@click.argument('tables', nargs=-1)
def stats(ctx: CliContext, tables: list) -> None:
    tables_api = ctx.upsolver_api().tables
    stats_screen(
        title='Table Stats',
        headers=[f.name for f in dataclasses.fields(entities.Table)],
        get_values=lambda: [
            t for t in tables_api.list()
            if (len(tables) == 0) or (t.name in tables) or (t.id in tables)
        ]
    )


@tables.command(help='Export a certain table as a "CREATE TABLE" sql command that can be '
                     'used in an "upsolver execute" command')
@click.pass_obj
@click.argument('table', nargs=1)
def export(ctx: CliContext, table: str) -> None:
    tables_api = ctx.upsolver_api().tables
    ctx.write(tables_api.export(find_by_name_or_id(table, tables_api.list()).id))


@tables.command(help='Display the partitions of a given table')
@click.pass_obj
@click.argument('table', nargs=1)
def partitions(ctx: CliContext, table: str) -> None:
    tables_api = ctx.upsolver_api().tables
    ctx.write(tables_api.get_partitions(find_by_name_or_id(table, tables_api.list()).id))
