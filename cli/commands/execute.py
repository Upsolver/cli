import click
from click import echo

from cli.commands.context import CliContext


@click.command()
@click.pass_obj
@click.argument('expression')
@click.option('-o', '--output-format', default='json',
              help='The format that the results will be returned in')
@click.option('-d', '--dry-run', is_flag=True, default=False,
              help='Validate expression is syntactically valid but don\'t run the command.')
def execute(
    ctx: CliContext,
    expression: str,
    output_format: str,
    dry_run: bool,
) -> None:
    """
    Execute a single SQL query
    """
    expression = expression.strip()
    if expression == '-':
        # TODO can't tell if stdin has input or not...
        #  (use select? problems with Windows-compatbaility...)
        expression = click.get_text_stream('stdin').read()

    if len(expression) == 0:
        return

    api = ctx.upsolver_api()
    if dry_run:
        check_result = api.check_syntax(expression)
        if len(check_result) > 0:
            check_result_txt = "\n".join(check_result)
            echo(err=True, message=f'found following errors in expression:\n{check_result_txt})')
        else:
            echo("Expression is valid.")
    else:
        result = api.execute(expression)
        ctx.write(result)
