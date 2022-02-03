import click

from cli.commands.context import CliContext
from cli.ui import stats_screen
from cli.upsolver.entities import Job


@click.group()
def jobs() -> None:
    """
    View & manage Jobs
    """
    pass


@jobs.command(help='List clusters')
@click.pass_obj
def ls(ctx: CliContext) -> None:
    ctx.write(ctx.upsolver_api().get_jobs())


@jobs.command(help='Display a live stream of jobs(s) statistics')
@click.pass_obj
@click.argument('jobs', nargs=-1)
def stats(ctx: CliContext, jobs: list[str]) -> None:
    api = ctx.upsolver_api()
    stats_screen(
        title='Job Stats',
        headers=list(Job._fields),
        get_values=lambda: [
            j for j in api.get_jobs()
            if (len(jobs) == 0) or (j.name in jobs)
        ]
    )


@jobs.command(help='Export a certain job as a "CREATE JOB" sql command that can be '
                   'used in an "upsolver execute" command')
@click.pass_obj
@click.argument('job', nargs=1)
def export(ctx: CliContext, job: str) -> None:
    ctx.echo(ctx.upsolver_api().export_job(job))
