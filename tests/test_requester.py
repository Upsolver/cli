import copy

import pytest
from pytest_mock import MockerFixture
from requests import Request
from yarl import URL

from cli.errors import ApiErr
from cli.upsolver.requester import AuthFiller, Requester


class TestAuthFiller(AuthFiller):
    TEST_HEADER = {'TestHeader': '123'}
    BAD_HEADER = {'BadHeader': '123'}

    def fill(self, req: Request) -> Request:
        # The idea here is to ensure that the Requester uses the returned Request object,
        # instead of the one it passes to `fill`. Since we can't enforce that implementations
        # of AuthFiller will implement `fill` as a pure function, we resort to enforcing that
        # it is used as if it were a pure function
        res = copy.deepcopy(req)
        res.headers = res.headers | self.TEST_HEADER

        # BAD_HEADER is present on the input req, but is not present on the result, making it
        # easy to verify that Requester uses the AuthFiller correctly.
        req.headers = req.headers | self.BAD_HEADER

        return res


def test_auth_filling(mocker: MockerFixture) -> None:
    """
    Test whether Requester fills in the authentication information correctly on the
    Request object, as specified by the custom AuthFiller defined for this test
    """
    mock_session = mocker.MagicMock()
    mock_session.prepare_request = lambda x: x
    mock_send = mock_session.send
    mock_resp = mocker.MagicMock(status_code=200)
    mock_send.return_value = mock_resp

    requester = Requester(URL('mock://localhost'), TestAuthFiller(), mock_session)
    requester.get('/test')

    send_headers = mock_send.call_args.args[0].headers

    assert TestAuthFiller.TEST_HEADER.items() <= send_headers.items()
    assert not(TestAuthFiller.BAD_HEADER.items() <= send_headers.items())


def test_response_validation(mocker: MockerFixture) -> None:
    mock_session = mocker.MagicMock()
    mock_session.prepare_request = lambda x: x
    mock_send = mock_session.send
    mock_resp = mocker.MagicMock(status_code=404)
    mock_send.return_value = mock_resp

    requester = Requester(URL('mock://localhost'), TestAuthFiller(), mock_session)

    with pytest.raises(ApiErr) as err:
        requester.get('/test')

    assert err.value.resp.status_code == 404
