import json
from abc import ABCMeta, abstractmethod
from enum import Enum
from json import JSONDecodeError
from pathlib import Path
from typing import Optional

from cli.upsolver.entities import Cluster
from cli.upsolver.requester import BetterResponse


class ExitCode(Enum):
    InternalErr = -999

    NetworkErr = -1
    ApiErr = -2
    ConfigurationErr = -3

    UserHasNoOrgs = -100

    ClusterNotFound = -101


"""
- CliErr: All errors thrown by upsolver cli code extend this class
- InternalErr: programming error / something went wrong
- ConfigErr: errors related to configuration (e.g. failure to read config from disk)
- RequestErr: sub-divides into two major classes:
  1. NetworkErr: something went wrong at the network layer (e.g. request timeout or invalid host)

  2. ApiErr: upsolver API reports an error (non 2XX response) e.g. invalid auth credentials. This
     class of errors also includes issues *with* upsolvers API, i.e. invalid/unexpected responses.

- OperationErr: API works as expected but the operation is invalid, e.g. attempting to delete a non
  existent cluster.


                                                     ┌──────┐
                                                     │CliErr│
                                                     └──────┘
                                                         ▲
                                                         │
          ┌──────────────────────┬───────────────────────┴───┬────────────────────────────────────────┐
          │                      │                           │                                        │
          │                      │                           │                                        │
   ┌─────────────┐         ┌───────────┐              ┌─────────────┐                         ┌───────────────┐
   │ InternalErr │         │ ConfigErr │              │ RequestErr  │                         │ OperationErr  │
   └─────────────┘         └───────────┘              └─────────────┘                         └───────────────┘
          ▲                      ▲                           ▲                                        ▲
          │                      │                           │                                        │
          │                      │                  ┌────────┴───────┐                     ┌──────────┴────────────┐
          │                      │                  │                │                     │                       │
          │                      │                  │                │                     │                       │
┌───────────────────┐    ┌───────────────┐   ┌────────────┐     ┌─────────┐        ┌───────────────┐     ┌──────────────────┐
│ NotImplementedErr │    │ConfigReadFail │   │ NetworkErr │     │ ApiErr  │        │ UserHasNoOrgs │     │ ClusterNotFound  │
└───────────────────┘    └───────────────┘   └────────────┘     └─────────┘        └───────────────┘     └──────────────────┘
                                                                     ▲
                                                      ┌──────────────┴───────────────┐
                                                      │                              │
                                            ┌───────────────────┐        ┌───────────────────────┐
                                            │ PayloadPathKeyErr │        │ PendingResultTimeout  │
                                            └───────────────────┘        └───────────────────────┘
"""


class CliErr(Exception, metaclass=ABCMeta):
    """
    Root of all Errors
    """

    @staticmethod
    @abstractmethod
    def exit_code() -> ExitCode:
        pass


class InternalErr(CliErr):
    @staticmethod
    def exit_code() -> ExitCode:
        return ExitCode.InternalErr


class NotImplementedErr(InternalErr):
    pass


# Configuration Errors
class ConfigErr(CliErr):
    @staticmethod
    def exit_code() -> ExitCode:
        return ExitCode.ConfigurationErr


class ConfigReadFail(ConfigErr):
    def __init__(self, path: Path, why: Optional[str] = None):
        super(ConfigReadFail, self).__init__(
            f'Failed to read configuration from {path}' + ('' if why is None else f': {why}')
        )


# Request Errors
class RequestErr(CliErr, metaclass=ABCMeta):
    """
    Generalized error that occured when issuing a request to the Upsolver API
    """
    pass


class NetworkErr(RequestErr):
    """
    Request has failed due to network issues, e.g. timeout, unknown host, etc. In other words,
    we don't have a valid http response object available.
    """

    @staticmethod
    def exit_code() -> ExitCode:
        return ExitCode.NetworkErr


class ApiErr(RequestErr):
    """
    Invalid usage of API (invalid credentials, bad method call). In other words, we have a valid
    http response object available and the status code is not 2XX.
    """

    @staticmethod
    def exit_code() -> ExitCode:
        return ExitCode.ApiErr

    def __init__(self, resp: BetterResponse):
        self.resp = resp

    def detail_message(self) -> Optional[str]:
        """
        Make an effort to provide a clean error message about why the API call failed.
        """
        try:
            j = json.loads(self.resp.text)
            if j.get('clazz') == 'ForbiddenException':
                return j.get('detailMessage')
            elif j.get('message') is not None:
                return j.get('message')
            else:
                # default to just returning the payload; not pretty but better than nothing
                return self.resp.text
        except JSONDecodeError:
            return self.resp.text

    def __str__(self) -> str:
        req_id_part = f', request_id={self.resp.request_id()}' \
            if self.resp.request_id() is not None \
            else ''

        return f'API Error [status_code={self.resp.status_code}{req_id_part}]: ' \
               f'{self.detail_message()}'


class PendingResultTimeout(ApiErr):
    def __init__(self, resp: BetterResponse):
        super().__init__(resp)

    def __str__(self) -> str:
        req_id_part = f', request_id={self.resp.request_id()}' \
            if self.resp.request_id() is not None \
            else ''

        return f'Timeout while waiting for results to become ready{req_id_part}'


class PayloadPathKeyErr(ApiErr):
    """
    describes failure to access some path within (json) dictionary of response's payload.
    """

    def __init__(self, resp: BetterResponse, bad_path: str):
        """
        :param resp: response object
        :param bad_path: e.g. "x.y.z" means we attempted to access field z within y within x
        """
        super().__init__(resp)
        self.bad_path = bad_path

    def __str__(self) -> str:
        req_id_part = f' [request_id={self.resp.request_id()}]' \
            if self.resp.request_id() is not None \
            else ''

        return f'Api Error{req_id_part}: failed to find {self.bad_path} in response payload' \
               f'{self.resp.payload}'


class OperationErr(RequestErr, metaclass=ABCMeta):
    """
    The operation that the request was meant to perform has failed, e.g. failing to delete a
    cluster.
    """
    pass


class UserHasNoOrgs(OperationErr):
    @staticmethod
    def exit_code() -> ExitCode:
        return ExitCode.UserHasNoOrgs

    def __init__(self, email: Optional[str] = None) -> None:
        self.email = email

    def __str__(self) -> str:
        email_part = f'{self.email} ' if self.email is not None else ''
        return f'User {email_part}has no organization available'


class ClusterNotFound(OperationErr):
    @staticmethod
    def exit_code() -> ExitCode:
        return ExitCode.ClusterNotFound

    def __init__(self, cluster_name: str, existing_clusters: list[Cluster]):
        self.cluster_name = cluster_name
        self.existing_clusters = existing_clusters

    def __str__(self) -> str:
        return f'Failed to find cluster named \'{self.cluster_name}\' in the following ' \
               f'list of available clusters: {",".join([c.name for c in self.existing_clusters])}'
