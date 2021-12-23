from typing import Optional

import click
from click import echo


@click.group()
def clusters() -> None:
    pass


@clusters.command(help='List clusters')
def ls() -> None:
    echo("running clusters ls ...")


@clusters.command(help='Display a live stream of cluster(s) usage statistics')
@click.option('-c', '--cluster', default=None, help='Name of cluster for which to show statistics')
def stats(cluster: Optional[str]) -> None:
    echo(f'running clusters stats (cluster={cluster}) ... ')
