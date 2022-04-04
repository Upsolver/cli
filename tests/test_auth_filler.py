import pytest
import requests

from cli.upsolver.auth_filler import AuthFiller, CredsAuthFiller, TokenAuthFiller

fillers: list[AuthFiller] = [
    CredsAuthFiller('email', 'password'),
    TokenAuthFiller('token')
]


@pytest.mark.parametrize('filler', fillers)
def test_creates_new_req_object(filler: AuthFiller):
    print(filler)
    before = requests.Request()
    after = filler(before)
    assert before is not after
