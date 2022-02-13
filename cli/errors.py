import json
from enum import Enum
from json import JSONDecodeError
from pathlib import Path
from typing import Optional

from cli.upsolver.entities import Cluster
from cli.upsolver.requester import BetterResponse


class InternalErr(Exception):
    pass


class BadArgument(ValueError):
    pass


class ConfigErr(Exception):
    pass


class ConfigReadFail(ConfigErr):
    def __init__(self, path: Path, why: Optional[str] = None):
        super(ConfigReadFail, self).__init__(
            f'Failed to read configuration from {path}' + ('' if why is None else f': {why}')
        )


class UserHasNoOrgs(Exception):
    def __init__(self, email: Optional[str] = None):
        self.email = email


class ApiErr(Exception):
    def __init__(self,
                 status_code: int,
                 request_id: str,
                 payload: str,
                 desc: Optional[str] = None):
        self.status_code = status_code
        self.request_id = request_id
        self.payload = payload
        self.desc = desc

    def detail_message(self) -> Optional[str]:
        """
        Make best effort to provide detailed error message about why API call failed
        """
        try:
            j = json.loads(self.payload)
            if j.get('clazz') == 'ForbiddenException':
                return j.get('detailMessage')
            else:
                # default to just returning the payload; not pretty but better than nothing
                return self.payload
        except JSONDecodeError:
            return self.payload


def api_err_from_resp(bresp: BetterResponse, desc: Optional[str] = None) -> ApiErr:
    return ApiErr(
        status_code=bresp.resp.status_code,
        request_id=bresp.request_id(),
        payload=bresp.text,
        desc=desc
    )


class Timeout(Exception):
    pass


class PayloadErr(ApiErr):
    pass


class ClusterNotFound(ApiErr):
    def __init__(self, cluster_name: str, existing_clusters: list[Cluster]):
        self.cluster_name = cluster_name
        self.existing_clusters = existing_clusters


class ExitCodes(Enum):
    GeneralError = -1
