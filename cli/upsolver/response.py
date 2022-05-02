from typing import Any, Optional

from requests import Response

from cli import errors
from cli.utils import NestedDictAccessor


class UpsolverResponse(object):
    """
    A wrapper around requests.Response object that adds some QoL methods.
    """

    def __init__(self, resp: Response):
        self.resp = resp

    def request_id(self) -> Optional[str]:
        return self.resp.headers.get('x-api-requestid')

    def __getattr__(self, attr: Any) -> Any:
        """
        UpsolverResponse is fully transparent proxy to actual Response object
        """
        return getattr(self.resp, attr)

    def __getitem__(self, item: str) -> Any:
        payload = self.resp.json()
        try:
            return NestedDictAccessor(payload)[item]
        except KeyError:
            raise errors.PayloadPathKeyErr(self, item)

    def get(self, item: str) -> Optional[Any]:
        try:
            return NestedDictAccessor(self.resp.json())[item]
        except KeyError:
            return None

    def __str__(self) -> str:
        return str(self.resp.json())
