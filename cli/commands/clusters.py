import click
from click import echo

from cli.commands.context import CliContext


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
@click.argument('clusters', nargs=-1)
def stats(clusters: list[str]) -> None:
    # TODO what endpoint to use for this? should get_clusters return Cluster object with this info
    #  or should we have a different endpoint specifically for stats?
    echo(f'running clusters stats (clusters=[{", ".join(clusters)}]) ... ')


@clusters.command(help='Export a certain cluster as a "CREATE CLUSTER" sql command that can be '
                       'used in an "upsolver execute" command')
@click.pass_obj
@click.argument('cluster', nargs=1)
def export(ctx: CliContext, cluster: str) -> None:
    echo(ctx.upsolver_api().export_cluster(cluster))


@clusters.command(help='Stop a cluster')
@click.pass_obj
@click.argument('cluster', nargs=1)
def stop(ctx: CliContext, cluster: str) -> None:
    echo(f'stopping {cluster} ...')
    ctx.upsolver_api().stop_cluster(cluster)


@clusters.command(help='Run a cluster')
@click.pass_obj
@click.argument('cluster', nargs=1)
def run(ctx: CliContext, cluster: str) -> None:
    echo(f'running cluster {cluster} ...')
    ctx.upsolver_api().run_cluster(cluster)


@clusters.command(help='Delete a cluster')
@click.pass_obj
@click.argument('cluster', nargs=1)
def rm(ctx: CliContext, cluster: str) -> None:
    echo(f'deleting cluster {cluster} ...')
    ctx.upsolver_api().delete_cluster(cluster)
