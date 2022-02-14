import copy
from abc import ABCMeta, abstractmethod
from typing import Any, Optional

from requests import Request, Response, Session
from yarl import URL

from cli.errors import ApiErr, PayloadErr, UserHasNoOrgs
from cli.ui import prompt_choose_dialog
from cli.utils import NestedDictAccessor


class AuthFiller(metaclass=ABCMeta):
    """
    To issue requests to upsolver API there needs to be some sort of authentiation data present
    on the request object. An implementation of AuthFiller takes a request object and returns a
    modified request object, one that has the relevant authentication info.

    Does not modify provided req object; returns modified copy.
    """
    @abstractmethod
    def fill(self, req: Request) -> Request:
        pass


class CredsAuthFiller(AuthFiller):
    EmailHeader = 'X-Api-Email'
    PasswordHeader = 'X-Api-Password'

    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password

    def fill(self, req: Request) -> Request:
        assert req.headers.get(CredsAuthFiller.EmailHeader) is None
        assert req.headers.get(CredsAuthFiller.PasswordHeader) is None
        filled = copy.deepcopy(req)
        filled.headers = filled.headers | {
            CredsAuthFiller.EmailHeader: self.email,
            CredsAuthFiller.PasswordHeader: self.password
        }
        return filled


class TokenAuthFiller(AuthFiller):
    TokenHeader = 'Authorization'

    def __init__(self, token: str) -> None:
        Request()
        self.token = token

    def fill(self, req: Request) -> Request:
        assert req.headers.get(TokenAuthFiller.TokenHeader) is None
        filled = copy.deepcopy(req)
        filled.headers = filled.headers | {TokenAuthFiller.TokenHeader: self.token}
        return filled


class BetterResponse(object):
    """
    A wrapper around requests.Response object that adds some QoL methods.
    """

    def __init__(self, resp: Response):
        self.resp = resp

    def request_id(self) -> str:
        try:
            return self.resp.headers['x-api-requestid']
        except KeyError:
            raise ApiErr(
                status_code=self.resp.status_code,
                request_id='',
                payload=self.resp.text,
                desc='API response has no request id header'
            )

    def __getattr__(self, attr: Any) -> Any:
        return getattr(self.resp, attr)

    def __getitem__(self, item: str) -> Any:
        payload = self.resp.json()
        try:
            return NestedDictAccessor(payload)[item]
        except KeyError:
            raise PayloadErr(
                status_code=self.resp.status_code,
                request_id=self.request_id(),
                payload=self.resp.text,
                desc=f'Failed to find {item} in response payload'
            )

    def get(self, item: str) -> Optional[Any]:
        try:
            return NestedDictAccessor(self.resp.json())[item]
        except KeyError:
            return None


def parse_url(url: Optional[str]) -> Optional[URL]:
    if url is None:
        return None

    burl = URL(url)
    if burl.is_absolute():
        return burl
    else:
        if url.startswith('localhost'):
            return URL('http://' + url)
        else:
            return URL('https://' + url)


class Requester(object):
    """
    A very thin wrapper around requests package that handles common errors and response
    transformations to usable objects (e.g. extracting payload as json automatically).

    Requester is not meant  "hide" the fact that we're using the requests package. It simply
    aggregates common behavior around issuing requests and handling responses, as well as providing
    tailor-made API for cli code.
    """

    @staticmethod
    def get_base_url(base_url: URL, token: str) -> URL:
        """
        Retrieve base_url with which further API calls should be made.
        """
        requester = Requester(base_url=base_url, auth_filler=TokenAuthFiller(token))

        user_info = requester.get('/users')
        curr_org = user_info.get('currentOrganization')
        if curr_org is None:
            orgs: Optional[list[dict[Any, Any]]] = user_info.get('organizations')
            if orgs is None or len(orgs) == 0:
                raise UserHasNoOrgs()

            curr_org = prompt_choose_dialog(
                'Choose active organization:',
                [(org, org['displayData']['name']) for org in orgs]
            )

            requester.put(f'/users/organizations/{curr_org["id"]}')

        return parse_url(requester.get('/environments/local-api')['dnsInfo.name'])

    @staticmethod
    def _normalize_path(path: str) -> str:
        return path if path.startswith('/') else f'/{path}'

    def __init__(self,
                 base_url: URL,
                 auth_filler: AuthFiller,
                 session: Optional[Session] = None):
        """
        :param base_url: all requests will be issued to this host
        :param auth_filler: will be used to modify Request objects prior to sending them in order to
        fill in authentication-related data (e.g. Authorization header).
        :param session: Requester uses a single session object to make requests with, and will use
        the provided one if it's not None.
        """
        self.base_url = base_url
        self.auth_filler = auth_filler
        self.sess = Session() if session is None else session

    def _build_url(self, path: str) -> str:
        return f'{str(self.base_url)}{self._normalize_path(path)}'

    def _preprepare(self, req: Request) -> Request:
        return self.auth_filler.fill(req)

    def _validate_response(self, resp: Response) -> Response:
        is_invalid_resp = int(resp.status_code / 100) != 2

        if is_invalid_resp:
            raise ApiErr(
                status_code=resp.status_code,
                request_id=BetterResponse(resp).request_id(),
                payload=resp.text
            )

        return resp

    def _send(self,
              path: str,
              req: Request,
              json: Optional[dict[Any, Any]] = None) -> BetterResponse:
        req.url = self._build_url(self._normalize_path(path))
        if json is not None:
            req.json = json

        return BetterResponse(self._validate_response(
            self.sess.send(self.sess.prepare_request(self._preprepare(req)))
        ))

    def get(self, path: str) -> BetterResponse:
        return self._send(path, Request(method='GET'))

    def put(self, path: str) -> BetterResponse:
        return self._send(path, Request(method='PUT'))

    def post(self, path: str, json: dict[Any, Any]) -> BetterResponse:
        return self._send(path, Request(method='POST'), json)

    def patch(self, path: str, json: dict[Any, Any]) -> BetterResponse:
        return self._send(path, Request(method='PATCH'), json)
