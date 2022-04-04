from pathlib import Path

import pytest
from requests_mock import Mocker as RequestsMocker
from yarl import URL

from cli.commands.context import CliContext
from cli.config import ConfigurationManager
from cli.errors import ApiErr
from tests.mock_upsolver_rest_api import DEFAULT_TOKEN, MockUpsolverRestApi


def test_authenticate_valid(requests_mock: RequestsMocker, tmp_path: Path) -> None:
    mock_api = MockUpsolverRestApi(requests_mock)
    mock_api.add_user('test@email.com', 'test123')

    ctx = CliContext(ConfigurationManager(tmp_path / 'conf'))
    auth_base_url = URL('http://localhost')
    profile_auth_settings = ctx.auth_api(auth_base_url).authenticate('test@email.com', 'test123')
    assert profile_auth_settings.base_url == auth_base_url
    assert profile_auth_settings.token == DEFAULT_TOKEN


def test_authenticate_invalid(requests_mock: RequestsMocker, tmp_path: Path) -> None:
    MockUpsolverRestApi(requests_mock)
    ctx = CliContext(ConfigurationManager(tmp_path / 'conf'))

    with pytest.raises(ApiErr) as err:
        ctx.auth_api().authenticate('test@email.com', 'test123')

    assert err.value.resp.status_code == 403
