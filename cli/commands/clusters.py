import dataclasses

import click

from cli.commands.context import CliContext
from cli.ui import stats_screen
from cli.upsolver.entities import Cluster
from cli.utils import find_by_name_or_id


@click.group()
def clusters() -> None:
    """
    View & manage compute clusters
    """
    pass


@clusters.command(help='List clusters')
@click.pass_obj
def ls(ctx: CliContext) -> None:
    ctx.write(ctx.upsolver_api().clusters.raw.get())


@clusters.command(help='Display a live stream of cluster(s) usage statistics')
@click.pass_obj
@click.argument('clusters', nargs=-1)
def stats(ctx: CliContext, clusters: list[str]) -> None:
    clusters_api = ctx.upsolver_api().clusters
    stats_screen(
        title='Cluster Stats',
        headers=[f.name for f in dataclasses.fields(Cluster)],
        get_values=lambda: [
            c for c in clusters_api.get()
            if (len(clusters) == 0) or (c.name in clusters)
        ]
    )


@clusters.command(help='Stop a cluster')
@click.pass_obj
@click.argument('cluster', nargs=1)
def stop(ctx: CliContext, cluster: str) -> None:
    clusters_api = ctx.upsolver_api().clusters
    clusters_api.stop(find_by_name_or_id(cluster, clusters_api.get()).id)


@clusters.command(help='Run a cluster')
@click.pass_obj
@click.argument('cluster', nargs=1)
def run(ctx: CliContext, cluster: str) -> None:
    clusters_api = ctx.upsolver_api().clusters
    clusters_api.run(find_by_name_or_id(cluster, clusters_api.get()).id)


@clusters.command(help='Delete a cluster')
@click.pass_obj
@click.argument('cluster', nargs=1)
def rm(ctx: CliContext, cluster: str) -> None:
    clusters_api = ctx.upsolver_api().clusters
    clusters_api.delete(find_by_name_or_id(cluster, clusters_api.get()).id)
