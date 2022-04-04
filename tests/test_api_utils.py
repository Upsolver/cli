from requests_mock import Mocker as RequestsMocker
from yarl import URL

from cli.upsolver.api_utils import get_base_url
from tests.mock_upsolver_rest_api import MockUpsolverRestApi


def test_get_base_url_no_dns_info(requests_mock: RequestsMocker) -> None:
    rest_api_mock = MockUpsolverRestApi(requests_mock)
    rest_api_mock.set_base_url(None)

    url = URL('http://localhost')
    assert get_base_url(URL('http://localhost'), 'token123') == url
