import click
from click import echo

from cli.commands.context import CliContext

# def formatify(input: str, input_fmt: str, desired_fmt: str) -> str:
#     return input


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

    # echo(ctx.confman.conf.active_profile)
    # TODO how to add support for running files

    # TODO format should be enum (idiomatic in python?)
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

        # # ctx.confman.conf.active_profile.output
        #
        # # TODO result is a string that is a json, will need to be converted to
        # #  w/e format is requested
        # formatted_result = formatify(result, input_fmt='json', desired_fmt=output_format)
        #
        # echo(f'executing command (output format: {output_format}) "{expression}"'
        #      f' ...\nresult: {formatted_result}')
