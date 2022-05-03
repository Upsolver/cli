import copy

import pytest
from requests import Request
from requests_mock import Mocker as RequestsMocker
from requests_mock import NoMockAddress
from yarl import URL

from cli.errors import ApiErr
from cli.upsolver.requester import Requester, default_resp_validator

# some tests check things that apply to all request methods. Such tests should be
# parameterized with this list (using @pytest.mark.parameterize).
requester_methods: list[str] = ['get', 'put', 'post', 'patch']


@pytest.mark.parametrize('method', requester_methods)
def test_path_formatting(requests_mock: RequestsMocker, method: str) -> None:
    """
    Requester has a "feature" where you can provide paths with leading '/' or without it.
    """
    getattr(requests_mock, method)('/users', text='success')

    r = Requester(URL('http://localhost'))
    assert getattr(r, method)('/users').text == 'success'
    assert getattr(r, method)('users').text == 'success'


@pytest.mark.parametrize(
    'sc_fail',  # tuples of (status_code, should_validation_fail)
    [(sc, False) for sc in [200, 201]] +
    [(sc, True) for sc in [300, 301, 400, 404, 503]]
)
@pytest.mark.parametrize('method', requester_methods)
def test_response_validation(
        requests_mock: RequestsMocker,
        sc_fail: tuple[int, bool],
        method: str) -> None:
    r = Requester(
        base_url=URL('http://localhost'),
        resp_validator=default_resp_validator
    )
    (sc, fail) = sc_fail

    path = f'/{sc}'
    getattr(requests_mock, method)(path, status_code=sc)

    r_method = getattr(r, method)
    if fail:
        with pytest.raises(ApiErr) as err:
            r_method(path)
        assert err.value.resp.status_code == sc
    else:
        assert r_method(path).status_code == sc


@pytest.mark.parametrize('method', requester_methods)
def test_auth_filling(requests_mock: RequestsMocker, method: str) -> None:
    expected_headers = {'test_header_k': 'test_header_v'}

    def dummy_auth_filler(r: Request) -> Request:
        res = copy.deepcopy(r)
        res.headers.update(expected_headers)
        return res

    r = Requester(
        base_url=URL('http://localhost'),
        auth_filler=dummy_auth_filler
    )

    getattr(requests_mock, method)('/users', request_headers=expected_headers, text='success')
    assert getattr(r, method)('/users').text == 'success'

    # try issuing request without filling in auth info to see it fails
    with pytest.raises(NoMockAddress):
        getattr(Requester(base_url=URL('http://localhost')), method)('/users')
