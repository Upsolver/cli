#!/usr/bin/env python
import hashlib
import subprocess
import urllib.request
from pathlib import Path
from string import Template
from typing import Optional

import click
import poet
import toml

import cli

DEFAULT_ARCHIVE_URL = f'https://github.com/Upsolver/cli/releases/download/stable/cli-{cli.__version__}.tar.gz'


@click.command(help='Generates brew Formula based on poetry.lock file')
@click.option('--cli-archive-url', default=DEFAULT_ARCHIVE_URL)
@click.option('--compute-hash-from-build', default=False, is_flag=True)
@click.option('--compute-hash-from-file', default=None)
@click.option('--poetry-lock-path', default=str(Path.cwd() / 'poetry.lock'))
@click.option('--formula-template-path', default=str(Path.cwd() / 'scripts/upsolver-cli.rb.template'))
@click.option('--formula-out-path', default=str(Path.cwd() / 'Formula/upsolver-cli.rb'))
def generate_brew_formula(cli_archive_url: str,
                          compute_hash_from_build: bool,
                          compute_hash_from_file: Optional[str],
                          poetry_lock_path: str,
                          formula_template_path: str,
                          formula_out_path: str) -> None:
    lock_content = toml.load(poetry_lock_path)

    # poet.py:141: PackageNotInstalledWarning: colorama is not installed so we cannot compute
    # resources for its dependencies.
    #   warnings.warn("{} is not installed so we cannot compute "
    blacklist = ['colorama']

    resources_txt = poet.resources_for([
        p['name']
        for p in lock_content['package']
        if p['category'] == 'main' and p['name'] not in blacklist
    ])

    cli_archive_url_for_hash = cli_archive_url
    if compute_hash_from_file is not None:
        cli_archive_url_for_hash = 'file://' + str(Path(compute_hash_from_file).resolve())
    elif compute_hash_from_build:
        build_res = subprocess.run(["poetry", "build"])
        if build_res.returncode != 0:
            print(f'Failed to build project, "poetry build" exited with code {build_res.returncode}')
            exit(build_res.returncode)

        cli_archive_url_for_hash = 'file://' + str(Path.cwd() / f'dist/cli-{cli.__version__}.tar.gz')

    with urllib.request.urlopen(cli_archive_url_for_hash) as cli_archive_f:
        archive_hash = hashlib.sha256(cli_archive_f.read()).hexdigest()

    print(f'computed hash {archive_hash} from archive url {cli_archive_url_for_hash}')

    with open(formula_template_path, 'r') as formula_template_f, \
         open(formula_out_path, 'w') as formula_out_f:
        formula_content = Template(formula_template_f.read()).substitute({
            'url': cli_archive_url,
            'url_sha256': archive_hash,
            'resources': resources_txt
        })

        print(f'Writing following content to {formula_out_path}:\n\n{formula_content}')
        formula_out_f.write(formula_content)


if __name__ == '__main__':
    generate_brew_formula()
