from pathlib import Path

import pytest
from requests_mock import Mocker as RequestsMocker

from cli.commands.context import CliContext
from cli.config import ConfigurationManager
from cli.errors import ApiErr
from cli.upsolver.entities import Catalog
from tests.mock_upsolver_rest_api import MockUpsolverRestApi


def test_get_catalogs(requests_mock: RequestsMocker, tmp_path: Path) -> None:
    rest_api_mock = MockUpsolverRestApi(requests_mock, tmp_path / 'conf')
    ctx = CliContext(ConfigurationManager(tmp_path / 'conf'))

    catalogs = ctx.upsolver_api().catalogs.list()
    assert len(catalogs) == 0

    c = Catalog('id0', 'name', 'created_by', 'kind', 'orgid')
    rest_api_mock.add_catalog(c)

    cs = ctx.upsolver_api().catalogs.list()
    assert len(cs) == 1
    assert cs == [c]


def test_get_catalogs_bad_status_code(requests_mock: RequestsMocker, tmp_path: Path) -> None:
    MockUpsolverRestApi(requests_mock, tmp_path / 'conf')
    requests_mock.get('/connections', status_code=403)

    ctx = CliContext(ConfigurationManager(tmp_path / 'conf'))

    with pytest.raises(ApiErr) as err:
        ctx.upsolver_api().catalogs.list()

    assert err.value.resp.status_code == 403
