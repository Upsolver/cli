from yarl import URL

from cli.errors import ApiUnavailable
from cli.upsolver.auth_filler import TokenAuthFiller
from cli.upsolver.requester import Requester
from cli.utils import parse_url


def get_base_url(base_url: URL, token: str) -> URL:
    """
    Retrieve base_url with which further API calls should be made.
    """
    requester = Requester(base_url=base_url, auth_filler=TokenAuthFiller(token))

    resp = requester.get('/environments/local-api')
    dns_name = resp.get('dnsInfo.name')
    if dns_name is None:
        raise ApiUnavailable(requester.base_url)

    return parse_url(dns_name)
