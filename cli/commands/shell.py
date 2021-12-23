import click

from cli.shell.shell import UpsolverShell
from cli.upsolver import build_upsolver_api


@click.command()
def shell() -> None:
    UpsolverShell(build_upsolver_api()).run_cli()
