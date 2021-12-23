import logging

import coloredlogs

from cli.config import Config


class CliContext(object):
    """
    This is used as the value for click.Context object that is passed to subcommands.

    CliContext holds "global" information (e.g. configuration) and is capable of spawning
    entities that depend on this configuration (e.g. loggers).
    """
    @staticmethod
    def _setup_logging() -> None:
        coloredlogs.install(level=logging.DEBUG)
        logging.basicConfig()

    def __init__(self, conf: Config):
        self._setup_logging()
        self.conf = conf

    def get_logger(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(self.conf.options.log_level.to_logging())
        return logger
