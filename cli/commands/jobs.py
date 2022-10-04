import dataclasses

import click

from cli.commands.context import CliContext
from cli.ui import stats_screen
from cli.upsolver.entities import Job
from cli.utils import find_by_name_or_id


@click.group()
def jobs() -> None:
    """
    View & manage Jobs
    """
    pass


@jobs.command(help='List jobs')
@click.pass_obj
def ls(ctx: CliContext) -> None:
    ctx.write(ctx.upsolver_api().jobs.raw.list())


@jobs.command(help='Display a live stream of jobs(s) statistics')
@click.pass_obj
@click.argument('jobs', nargs=-1)
def stats(ctx: CliContext, jobs: list) -> None:
    jobs_api = ctx.upsolver_api().jobs
    stats_screen(
        title='Job Stats',
        headers=[f.name for f in dataclasses.fields(Job)],
        get_values=lambda: [
            j for j in jobs_api.list()
            if (len(jobs) == 0) or (j.name in jobs) or (j.id in jobs)
        ]
    )


@jobs.command(help='Export a certain job as a "CREATE JOB" sql command that can be '
                   'used in an "upsolver execute" command')
@click.pass_obj
@click.argument('job', nargs=1)
def export(ctx: CliContext, job: str) -> None:
    jobs_api = ctx.upsolver_api().jobs
    ctx.write(jobs_api.export(find_by_name_or_id(job, jobs_api.list()).id))
