import click

from cli.commands.context import CliContext
from cli.ui import stats_screen
from cli.upsolver.entities import Cluster


@click.group()
def clusters() -> None:
    """
    View & manage compute clusters
    """
    pass


@clusters.command(help='List clusters')
@click.pass_obj
def ls(ctx: CliContext) -> None:
    ctx.write(ctx.upsolver_api().get_clusters())


@clusters.command(help='Display a live stream of cluster(s) usage statistics')
@click.pass_obj
@click.argument('clusters', nargs=-1)
def stats(ctx: CliContext, clusters: list[str]) -> None:
    api = ctx.upsolver_api()
    stats_screen(
        title='Cluster Stats',
        headers=list(Cluster._fields),
        get_values=lambda: [
            c for c in api.get_clusters()
            if (len(clusters) == 0) or (c.name in clusters)
        ]
    )


@clusters.command(help='Export a certain cluster as a "CREATE CLUSTER" sql command that can be '
                       'used in an "upsolver execute" command')
@click.pass_obj
@click.argument('cluster', nargs=1)
def export(ctx: CliContext, cluster: str) -> None:
    ctx.echo(ctx.upsolver_api().export_cluster(cluster))


@clusters.command(help='Stop a cluster')
@click.pass_obj
@click.argument('cluster', nargs=1)
def stop(ctx: CliContext, cluster: str) -> None:
    ctx.upsolver_api().stop_cluster(cluster)


@clusters.command(help='Run a cluster')
@click.pass_obj
@click.argument('cluster', nargs=1)
def run(ctx: CliContext, cluster: str) -> None:
    ctx.upsolver_api().run_cluster(cluster)


@clusters.command(help='Delete a cluster')
@click.pass_obj
@click.argument('cluster', nargs=1)
def rm(ctx: CliContext, cluster: str) -> None:
    ctx.upsolver_api().delete_cluster(cluster)
