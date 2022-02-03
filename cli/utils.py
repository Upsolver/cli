from pathlib import Path
from typing import Any, Optional

from requests import Response
from yarl import URL

from cli.errors import ApiErr


# TODO should be part of Requester
def get_payload(action_desc: str, r: Response) -> dict[Any, Any]:
    """
    Ensure that the response is valid and return the json payload as a dictionary.
    """
    if r.status_code != 200:
        raise ApiErr(f'Failed to {action_desc}, status code: {r.status_code}')

    return r.json()


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


def ensure_exists(path: Path) -> None:
    if not path.exists():
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        path.touch()
