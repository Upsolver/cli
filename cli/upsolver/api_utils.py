from typing import Optional

from yarl import URL

from cli import errors
from cli.ui import prompt_choose_dialog
from cli.upsolver.auth_filler import TokenAuthFiller
from cli.upsolver.requester import Requester
from cli.utils import parse_url


def ensure_user_has_curr_org(requester: Requester) -> None:
    """
    Uses requester to obtain information about user (requester contains an internal "auth"
    mechanism that identifies the user) and verifies the user has a current organization set.

    If the user does not have a "current organization" set, asks for the user to select one from
    a list of available organizations.

    This check / flow should be performed before any further actions with the API can be performed,
    since not having a "current organization" set will result in errors.
    """
    user_info = requester.get('/users')
    curr_org = user_info.get('currentOrganization')
    if curr_org is None:
        orgs: Optional[list] = user_info.get('organizations')
        if orgs is None or len(orgs) == 0:
            raise errors.UserHasNoOrgs(email=user_info.get('user.email'))

        curr_org = prompt_choose_dialog(
            'Choose active organization:',
            [(org, org['displayData']['name']) for org in orgs]
        )

        requester.put(f'/users/organizations/{curr_org["id"]}')


def get_base_url(base_url: URL, token: str) -> URL:
    """
    Retrieve base_url with which further API calls should be made.
    """
    requester = Requester(base_url=base_url, auth_filler=TokenAuthFiller(token))

    resp = requester.get('/environments/local-api')
    dns_name = resp.get('dnsInfo.name')
    if dns_name is None:
        # raise PrivateApiUnavailable(requester.base_url)
        return base_url  # default to using the auth endpoint as base url for api requests

    return parse_url(dns_name)
