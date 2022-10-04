import copy
from typing import Callable

from requests import Request

"""
To issue requests to upsolver API there needs to be some sort of authentiation data present
on the request object. An implementation of AuthFiller takes a request object and returns a
modified request object, one that has the relevant authentication info.

Does not modify provided req object; returns modified copy.
"""
AuthFiller = Callable[[Request], Request]


class CredsAuthFiller(object):
    EmailHeader = 'X-Api-Email'
    PasswordHeader = 'X-Api-Password'

    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password

    def __call__(self, req: Request) -> Request:
        assert req.headers.get(CredsAuthFiller.EmailHeader) is None
        assert req.headers.get(CredsAuthFiller.PasswordHeader) is None
        filled = copy.deepcopy(req)
        filled.headers.update({
            CredsAuthFiller.EmailHeader: self.email,
            CredsAuthFiller.PasswordHeader: self.password
        })
        return filled


class TokenAuthFiller(object):
    TokenHeader = 'Authorization'

    def __init__(self, token: str) -> None:
        self.token = token

    def __call__(self, req: Request) -> Request:
        assert req.headers.get(TokenAuthFiller.TokenHeader) is None
        filled = copy.deepcopy(req)
        filled.headers.update({TokenAuthFiller.TokenHeader: self.token})
        return filled
