import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, Optional

from click import echo
from yarl import URL

from cli.config import (
    Config,
    ConfigurationManager,
    LogLvl,
    ProfileAuthSettings,
    get_auth_settings,
)
from cli.errors import ConfigErr
from cli.formatters import Formatter
from cli.upsolver.api import UpsolverApi
from cli.upsolver.api_builder import build_upsolver_api
from cli.upsolver.api_utils import get_base_url
from cli.upsolver.auth import AuthApi, RestAuthApi
from cli.upsolver.auth_filler import TokenAuthFiller
from cli.upsolver.lexer import QueryLexer, SimpleQueryLexer
from cli.upsolver.requester import Requester
from cli.utils import ensure_exists, get_logger


def init_logging(conf: Config) -> None:
    log = get_logger()

    lvl = (
        LogLvl.DEBUG if conf.verbose
        else (conf.options.log_level if conf.options is not None else LogLvl.CRITICAL)
    ).to_logging()

    log.setLevel(lvl)

    formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')

    handlers: list = []
    if conf.options is not None:
        ensure_exists(conf.options.log_file)
        handlers.append(RotatingFileHandler(
            filename=conf.options.log_file,
            maxBytes=2 * (2 ** 20),
        ))

    # if verbose mode, also write to stderr
    if conf.verbose:
        log.setLevel(logging.DEBUG)
        handlers.append(logging.StreamHandler())

    for h in handlers:
        h.setLevel(lvl)
        h.setFormatter(formatter)
        log.addHandler(h)


class CliContext(object):
    """
    This is used as the value for click.Context object that is passed to subcommands.

    CliContext holds "global" information (e.g. configuration) and is capable of spawning
    entities that depend on this configuration.

    Also serves as the builder of UpsolverApi from more basic api components.

    Reasoning behind having two API builder methods, one for auth api and another one for the
    "whole" upsolver api:
    all api components depend on authentication api, and so we need to instantiate it before all
    others and use it, and with the results of calling it we are able to construct the other
    components.
    """

    def __init__(self, confman: ConfigurationManager):
        self.confman = confman
        init_logging(self.confman.conf)

    def query_lexer(self) -> QueryLexer:
        return SimpleQueryLexer()

    def auth_api(self, auth_base_url: Optional[URL] = None) -> AuthApi:
        if auth_base_url is None:
            auth_base_url = ConfigurationManager.CLI_DEFAULT_BASE_URL
        assert auth_base_url.is_absolute()

        return RestAuthApi(auth_base_url)

    def upsolver_api(self, auth_settings: Optional[ProfileAuthSettings] = None) -> UpsolverApi:
        auth_settings = auth_settings or get_auth_settings(self.confman.conf.active_profile)

        if auth_settings is None:
            raise ConfigErr('Could not find authentication settings, '
                            'please use the `configure` sub-command to create a profile.')

        return build_upsolver_api(
            requester=Requester(
                base_url=get_base_url(auth_settings.base_url, auth_settings.token),
                auth_filler=TokenAuthFiller(auth_settings.token)
            )
        )

    def write(self, x: Any, fmt: Optional[Formatter] = None) -> None:
        echo(
            message=fmt(x) if fmt is not None else self.confman.get_formatter()(x),
            file=sys.stdout
        )

    def exit(self, msg: str, code: int) -> None:
        echo(err=True, message=msg)
        sys.exit(code)
