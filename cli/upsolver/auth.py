import datetime
from abc import ABCMeta, abstractmethod
from typing import Any, Optional

from yarl import URL

from cli.config import ProfileAuthSettings
from cli.errors import InternalErr, UserHasNoOrgs
from cli.ui import prompt_choose_dialog
from cli.upsolver.requester import CredsAuthFiller, Requester


class AuthApi(metaclass=ABCMeta):
    @abstractmethod
    def authenticate(self, email: str, password: str) -> ProfileAuthSettings:
        pass


class InvalidAuthApi(AuthApi):
    """
    This type is used to construct UpsolverApi implementations that are not expected to be able
    to authenticate users. Since authentication and other api actions are currently separated,
    it marks a logical error to authenticate outside configuration (i.e. auth token retrieval)
    phase.
    """
    def authenticate(self, email: str, password: str) -> ProfileAuthSettings:
        raise InternalErr('This is a mistake, fix me.')


class RestAuthApi(AuthApi):
    """
    Responsible for performing authentication and holding up-to-date auth info
    required for making further calls to Upsolver API.
    """

    def __init__(self, base_url: URL) -> None:
        self.base_url = base_url

    def authenticate(self, email: str, password: str) -> ProfileAuthSettings:
        requester = Requester(self.base_url, CredsAuthFiller(email, password))

        user_info = requester.get('/users')
        curr_org = user_info.get('currentOrganization')

        if curr_org is None:
            orgs: Optional[list[dict[Any, Any]]] = user_info.get('organizations')
            if orgs is None or len(orgs) == 0:
                raise UserHasNoOrgs(email=email)

            curr_org = prompt_choose_dialog(
                'Choose active organization:',
                [(org, org['displayData']['name']) for org in orgs]
            )

            requester.put(f'/users/organizations/{curr_org["id"]}')

        api_token = requester.post(
            path='/api-tokens',
            json={
                'displayData': {
                    'name': f'apitoken-{email}-{datetime.datetime.now().timestamp()}',
                    'description': 'CLI generated token'
                }
            }
        )['apiToken']

        return ProfileAuthSettings(token=api_token, base_url=self.base_url)
