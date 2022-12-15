import json
from abc import ABCMeta, abstractmethod
from enum import Enum
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Optional

from yarl import URL

from cli.upsolver.requester import UpsolverResponse


class ExitCode(Enum):
    InternalErr = -999

    NetworkErr = -1
    ApiErr = -2
    ConfigurationErr = -3
    ApiUnavailable = -4
    InvalidOption = -5

    UserHasNoOrgs = -100
    EntityNotFound = -101


"""
- CliErr: All errors thrown by upsolver cli code extend this class. It can be easily mapped to an
  exit code, which serves to make automation easier (cli tooling can work with the exit code
  instead of checking for specific error messages).

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

    def __str__(self) -> str:
        # make an effort to extract a message
        for msg in [m for m in self.args if type(m) == str]:
            return msg

        return self.__class__.__name__


class InvalidOptionErr(CliErr):
    @staticmethod
    def exit_code() -> ExitCode:
        return ExitCode.InvalidOption


class InternalErr(CliErr):
    @staticmethod
    def exit_code() -> ExitCode:
        return ExitCode.InternalErr


class NotImplementedErr(InternalErr):
    pass


class FormattingErr(InternalErr):
    def __init__(self, v: Any, desired_fmt: str) -> None:
        """
        :param v: The value which caused the formatting error
        """
        self.v = v


# Configuration Errors
class ConfigErr(CliErr):
    @staticmethod
    def exit_code() -> ExitCode:
        return ExitCode.ConfigurationErr


class ConfigReadFail(ConfigErr):
    def __init__(self, path: Path, why: Optional[str] = None):
        self.path = path
        self.why = why

    def __str__(self) -> str:
        return f'Failed to read configuration from {self.path}' + \
               ('' if self.why is None else f': {self.why}')


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

    def __init__(self, resp: UpsolverResponse) -> None:
        self.resp = resp

    def detail_message(self) -> Optional[str]:
        """
        Make an effort to provide a clean error message about why the API call failed.
        """
        try:
            j = json.loads(self.resp.text)
            if type(j) is str:
                return j
            elif j is not None and j.get('clazz') == 'ForbiddenException':
                return j.get('detailMessage')
            elif j is not None and j.get('message') is not None:
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


class AuthErr(ApiErr):
    def __str__(self) -> str:
        return 'Authentication error, please run \'login\' command to create a valid token'


class PendingResultTimeout(ApiErr):
    def __init__(self, resp: UpsolverResponse):
        super().__init__(resp)

    def __str__(self) -> str:
        req_id_part = f', request_id={self.resp.request_id()}' \
            if self.resp.request_id() is not None \
            else ''

        return f'Timeout while waiting for results to become ready{req_id_part}'


class PayloadErr(ApiErr):
    def __init__(self, resp: UpsolverResponse, msg: str):
        super().__init__(resp)
        self.msg = msg

    def __str__(self) -> str:
        return f'Payload err ({self.msg}): {self.resp}'


class PayloadPathKeyErr(ApiErr):
    """
    describes failure to access some path within (json) dictionary of response's payload.
    """

    def __init__(self, resp: UpsolverResponse, bad_path: str):
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


class OperationErr(CliErr, metaclass=ABCMeta):
    pass


class ApiUnavailable(OperationErr):
    @staticmethod
    def exit_code() -> ExitCode:
        return ExitCode.ApiUnavailable

    def __init__(self, base_url: URL) -> None:
        self.base_url = base_url

    def __str__(self) -> str:
        return f'Failed to retrieve API address from {self.base_url}'


class UserHasNoOrgs(OperationErr):
    @staticmethod
    def exit_code() -> ExitCode:
        return ExitCode.UserHasNoOrgs

    def __init__(self, email: Optional[str] = None) -> None:
        self.email = email

    def __str__(self) -> str:
        email_part = f'{self.email} ' if self.email is not None else ''
        return f'User {email_part}has no organization available'


class EntityNotFound(OperationErr):
    @staticmethod
    def exit_code() -> ExitCode:
        return ExitCode.EntityNotFound

    def __init__(self, name: str, existing: Optional[list]):
        self.name = name
        self.existing = existing

    def __str__(self) -> str:
        if self.existing is not None:
            return f'Failed to find \'{self.name}\' in the following ' \
                   f'list of available entities: {", ".join(self.existing)}'
        else:
            return f'Failed to find \'{self.name}\''
