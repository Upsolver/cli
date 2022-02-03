from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner
from pytest_mock import MockerFixture

from cli import __version__
from cli.commands.catalogs import catalogs
from cli.commands.context import CliContext
from cli.config import ConfigurationManager
from cli.errors import ApiErr
from cli.upsolver import Catalog


def test_version():
    assert __version__ == '0.1.0'


def test_catalogs_ls_no_auth(tmp_path: Path) -> None:
    ctx = CliContext(ConfigurationManager(tmp_path / 'conf'))
    runner = CliRunner()
    result = runner.invoke(catalogs, ['ls'], obj=ctx)
    assert isinstance(result.exception, ApiErr)
    assert 'Missing auth' in str(result.exception)


def test_catalogs_ls(mocker: MockerFixture, tmp_path: Path) -> None:
    conf_path = tmp_path / 'conf'
    with open(conf_path, 'w') as conf_f:
        conf_f.write('''[profile]
token = token1234
base_url = localhost:8080
output = JSON''')

    ctx = CliContext(ConfigurationManager(conf_path))
    runner = CliRunner()

    c = Catalog(id='id0', name='c0', created_by='bob', kind='S3', orgId='orgid0')

    api = mocker.MagicMock()
    api.get_catalogs = mocker.MagicMock(
        return_value=[c]
    )

    with patch.object(ctx, 'upsolver_api', return_value=api):
        result = runner.invoke(catalogs, ['ls'], obj=ctx)
        api.get_catalogs.assert_called_once()
        assert result.stdout == ctx.confman.get_formatter()(c) + '\n'


def test_catalogs_ls_csv():
    pass
