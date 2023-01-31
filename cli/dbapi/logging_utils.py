import logging
from sys import stderr

LOG_NAME = "pep249-upsolver"
DEFAULT_LOGLEVEL = logging.DEBUG
logger = logging.getLogger(LOG_NAME)
logger.setLevel(DEFAULT_LOGLEVEL)
handler = logging.StreamHandler(stderr)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
