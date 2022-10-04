import uuid
from typing import Callable, Optional

from requests import Request, Response, Session
from yarl import URL

from cli import errors
from cli.upsolver.auth_filler import AuthFiller
from cli.upsolver.response import UpsolverResponse
from cli.utils import get_logger

"""
ResponseValidator gets a response, checks it, and returns it if everything is ok. If something
is wrong (e.g. status code is invalid) it raises an Exception
"""
ResponseVaidator = Callable[[Response], Response]


def default_resp_validator(resp: Response) -> Response:
    uresp = UpsolverResponse(resp)
    if resp.status_code == 403:
        raise errors.AuthErr(uresp)
    if int(resp.status_code / 100) != 2:
        raise errors.ApiErr(uresp)
    return resp


class Requester(object):
    """
    A very thin wrapper around requests package that handles common errors and response
    transformations to usable objects (e.g. extracting payload as json automatically).

    Requester is not meant  "hide" the fact that we're using the requests package. It simply
    aggregates common behavior around issuing requests and handling responses.

    Requester is intended to be solely used for issuing requests to Upsolver's API.
    """

    @staticmethod
    def _normalize_path(path: str) -> str:
        return path if path.startswith('/') else f'/{path}'

    def __init__(self,
                 base_url: URL,
                 auth_filler: Optional[AuthFiller] = None,
                 resp_validator: Optional[ResponseVaidator] = default_resp_validator):
        """
        :param base_url: all requests will be issued to this host
        :param auth_filler: will be used to modify Request objects prior to sending them in order to
        fill in authentication-related data (e.g. Authorization header).
        """
        self.base_url = base_url
        self.auth_filler = auth_filler if auth_filler is not None else lambda x: x
        self.resp_validator = resp_validator if resp_validator is not None else lambda x: x

        self.sess = Session()  # all requests will be issued using this Session object
        self.log = get_logger('Requester')

    def _build_url(self, path: str) -> str:
        return f'{str(self.base_url)}{self._normalize_path(path)}'

    def _preprepare(self, req: Request) -> Request:
        return self.auth_filler(req)

    def _send(self,
              path: str,
              req: Request,
              json: Optional[dict] = None) -> UpsolverResponse:
        # used to correlate request and response in the logs, at least for now
        req_id = str(uuid.uuid4())

        req.url = self._build_url(self._normalize_path(path))
        if json is not None:
            req.json = json

        prepared_req = self.sess.prepare_request(self._preprepare(req))
        self.log.debug(
            f'\nREQUEST (req_id={req_id}):\n'
            f'\tMETHOD={prepared_req.method}\n'
            f'\tURL={prepared_req.url}\n'
            f'\tHEADERS={prepared_req.headers}\n'
            f'\tBODY={str(prepared_req.body)}\n'
        )

        try:
            resp = self.sess.send(prepared_req)
        except Exception as ex:
            self.log.debug(f'REQUEST FAILED (req_id={req_id}): {ex}')
            raise ex

        self.log.debug(
            f'\nRESPONSE (req_id={req_id}):\n'
            f'\tSTATUS_CODE={resp.status_code}\n'
            f'\tHEADERS={resp.headers}\n'
            f'\tTEXT={resp.text}\n',
        )

        return UpsolverResponse(self.resp_validator(resp))

    def get(self, path: str) -> UpsolverResponse:
        return self._send(path, Request(method='GET'))

    def put(self, path: str) -> UpsolverResponse:
        return self._send(path, Request(method='PUT'))

    def post(self, path: str, json: Optional[dict] = None) -> UpsolverResponse:
        payload = json if json is not None else {}
        return self._send(path, Request(method='POST'), payload)

    def patch(self, path: str, json: Optional[dict] = None) -> UpsolverResponse:
        payload = json if json is not None else {}
        return self._send(path, Request(method='PATCH'), payload)

    def get_list(self, path: str, list_field_name: Optional[str] = None) -> list:
        resp = self.get(path)

        def raise_err() -> None:
            raise errors.PayloadErr(resp, 'expected list of elements')

        try:
            j = resp.json()

            # if given a list_field_name, look for the list there and only there
            if list_field_name is not None:
                if type(j) is not dict or j.get(list_field_name) is None:
                    raise_err()
                else:
                    return j[list_field_name]

            # otherwise, the entire response body must be the list
            if type(j) is list:
                return j

            # unknown payload
            raise_err()
        except Exception:
            raise_err()

        return []  # placate mypy
