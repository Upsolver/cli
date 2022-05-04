from pathlib import Path

import pytest
from requests_mock import Mocker as RequestsMocker

from cli.commands.context import CliContext
from cli.config import ConfigurationManager
from cli.errors import PendingResultTimeout
from tests.mock_upsolver_rest_api import MockUpsolverRestApi


def test_timeout(requests_mock: RequestsMocker, tmp_path: Path) -> None:
    MockUpsolverRestApi(requests_mock, tmp_path / 'conf')
    current_req_id = 'r123'
    resp_payload = {'status': 'Pending', 'current': current_req_id}
    requests_mock.post('/query', json=resp_payload, status_code=201)
    requests_mock.get(f'/{current_req_id}', json=resp_payload, status_code=201)

    api = CliContext(ConfigurationManager(tmp_path / 'conf')).upsolver_api()

    with pytest.raises(PendingResultTimeout):
        list(api.execute('SELECT * FROM something', timeout_sec=1.0))
