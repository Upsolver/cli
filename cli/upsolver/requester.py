from typing import Any

import requests
from requests import Response
from yarl import URL

from cli.errors import ApiErr


# TODO refactor
class Requester(object):
    """
    A very thin wrapper around requests package that handles common errors and response
    transformations to usable objects (e.g. extracting payload as json automatically).

    Requester is not meant  "hide" the fact that we're using the requests package. It simply
    aggregates common behavior around issuing requests and handling responses, as well as providing
    tailor-made API for cli code.
    """
    def __init__(self, auth_token: str, base_url: URL):
        self.auth_token = auth_token
        self.base_url = base_url

    @staticmethod
    def _normalize_path(path: str) -> str:
        return path if path.startswith('/') else f'/{path}'

    def _build_url(self, path: str) -> str:
        return f'{str(self.base_url)}{self._normalize_path(path)}'

    def get(self, path: str) -> Response:
        try:
            return requests.get(
                url=self._build_url(self._normalize_path(path)),
                headers={'Authorization': self.auth_token}
            )
        except Exception as ex:
            raise ApiErr(ex)

    def put(self, path: str) -> Response:
        try:
            return requests.put(
                url=self._build_url(self._normalize_path(path)),
                headers={'Authorization': self.auth_token}
            )
        except Exception as ex:
            raise ApiErr(ex)

    def post(self, path: str, json: dict[Any, Any]) -> Response:
        try:
            return requests.post(
                url=self._build_url(self._normalize_path(path)),
                headers={'Authorization': self.auth_token},
                json=json
            )
        except Exception as ex:
            raise ApiErr(ex)

    def patch(self, path: str, json: dict[Any, Any]) -> Response:
        try:
            return requests.post(
                url=self._build_url(self._normalize_path(path)),
                headers={'Authorization': self.auth_token},
                json=json
            )
        except Exception as ex:
            raise ApiErr(ex)
