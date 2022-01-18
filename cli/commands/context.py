import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, Optional

from click import echo
from yarl import URL

from cli.config import Config, ConfMan, LogLvl, get_auth_settings
from cli.upsolver import UpsolverApi, UpsolverRestApi

# class ICliContext(metaclass=ABCMeta):
#     confman: IConfMan
#     log: logging.Logger
#
#     @abstractmethod
#     def upsolver_api(self, auth_base_url: Optional[str] = None) -> UpsolverApi:
#         pass
#
#     @abstractmethod
#     def write(self, x: Any) -> None:
#         pass
#
#     @abstractmethod
#     def echo(self, msg: str) -> None:
#         pass
#
#
# class TestCliContext(ICliContext):
#     def __init__(self, api: UpsolverApi):
#         self.api = api
#         self.confman = TestConfMan()
#
#     def upsolver_api(self, auth_base_url: Optional[str] = None) -> UpsolverApi:
#         pass
#
#     def write(self, x: Any) -> None:
#         pass
#
#     def echo(self, msg: str) -> None:
#         pass


class CliContext(object):
    """
    This is used as the value for click.Context object that is passed to subcommands.

    CliContext holds "global" information (e.g. configuration) and is capable of spawning
    entities that depend on this configuration (e.g. upsolver api).
    """
    def _setup_logging(self, conf: Config) -> None:
        self.log = logging.getLogger('CLI')

        lvl = (
            LogLvl.DEBUG if conf.debug
            else (conf.options.log_level if conf.options is not None else LogLvl.CRITICAL)
        ).to_logging()
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')

        handlers: list[logging.Handler] = []
        if conf.options is not None:
            handlers.append(RotatingFileHandler(
                filename=conf.options.log_file,
                maxBytes=10 * (2 ** 20),
            ))

        # if debug mode, also write to stderr
        if conf.debug:
            handlers.append(logging.StreamHandler())

        for h in handlers:
            h.setLevel(lvl)
            h.setFormatter(formatter)
            self.log.addHandler(h)

    def __init__(self, confman: ConfMan):
        self.confman = confman
        self._setup_logging(self.confman.conf)

    def upsolver_api(self, auth_base_url: Optional[URL] = None) -> UpsolverApi:
        """
        :param auth_base_url: used for initial authentication
        :return: an implementation of UpsolverApi's interface.
        """
        return UpsolverRestApi(
            auth_base_url=(
                auth_base_url if auth_base_url is not None
                else ConfMan.CLI_DEFAULT_BASE_URL
            ),
            auth_settings=get_auth_settings(self.confman.conf.active_profile),
        )

    def write(self, x: Any) -> None:
        echo(message=self.confman.get_formatter()(x), file=sys.stdout)

    def echo(self, msg: str) -> None:
        echo(msg)

    # def authenticate(self, email: str, password: str, base_url: Optional[str]) -> None:
    #     api = self.upsolver_api(base_url)
    #     profile_auth_settings = api.authenticate(email, password)
    #     updated_profile = profile_auth_settings.update(self.confman.conf.active_profile)
    #     self.confman.update_profile(updated_profile)
    #     self.echo(
    #         f'Successfully performed authentication for profile \'{updated_profile.name}\' '
    #         f'(auth token: {updated_profile.token}, base url: {updated_profile.base_url})'
    #     )

    # def fmt(self, obj: NamedTuple) -> str:
    #     """
    #     TODO not sure this is the right place for this
    #       also: does it make sense to have "Cluster" etc.? or should I just work with raw json
    #       (i.e. dict) and so the transformers will always get a dictionary as input and output it?
    #       maybe formatter will also know which fields are relevant from the response?
    #       although sometimes that knowledge exists only at the api call scope...
    #
    #     format any object for output.
    #     affected by: User can change output formats (e.g. JSON, CSV)
    #     """
    #     json.dump
    #     desired_fmt = self.confman.conf.active_profile.output
    #     if desired_fmt == OutputFmt.JSON:
    #         return json.dumps(obj._asdict())
    #     else:
    #         raise InternalErr(f'Unsupported output format: {desired_fmt}')
    #
