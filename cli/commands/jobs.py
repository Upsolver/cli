import click
from click import echo

from cli.commands.context import CliContext


@click.group()
def jobs() -> None:
    pass


@jobs.command(help='List clusters')
@click.pass_obj
def ls(ctx: CliContext) -> None:
    echo('\n'.join([c.name for c in ctx.upsolver_api().get_jobs()]))


@jobs.command(help='Display a live stream of jobs(s) statistics')
@click.argument('jobs', nargs=-1)
def stats(jobs: list[str]) -> None:
    echo(f'running jobs stats (jobs={", ".join(jobs)}]) ... ')


@jobs.command(help='Export a certain job as a "CREATE JOB" sql command that can be '
                   'used in an "upsolver execute" command')
@click.pass_obj
@click.argument('job', nargs=1)
def export(ctx: CliContext, job: str) -> None:
    echo(ctx.upsolver_api().export_job(job))
