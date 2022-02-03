import datetime
from abc import ABCMeta, abstractmethod
from typing import Any, Optional

import requests
from yarl import URL

from cli.config import ProfileAuthSettings, parse_url
from cli.errors import ApiErr
from cli.ui import prompt_choose_dialog
from cli.utils import get_payload


class AuthApi(metaclass=ABCMeta):
    @abstractmethod
    def authenticate(self, email: str, password: str) -> ProfileAuthSettings:
        pass

    @staticmethod
    def get_base_url(auth_settings: ProfileAuthSettings) -> URL:
        """
        Retrieve base_url with to which further API calls should be made.
        """
        return parse_url(
            get_payload(
                'get base url for API calls',
                requests.get(
                    url=str(auth_settings.base_url / 'environments' / 'local-api'),
                    headers={'Authorization': auth_settings.token}
                )
            )['dnsInfo']['name']
        )


class RestAuthApi(AuthApi):
    auth_base_url: URL

    """
    Responsible for performing authentication and holding up-to-date auth info
    required for making further calls to Upsolver API.
    """

    def __init__(self, auth_base_url: URL) -> None:
        assert auth_base_url.is_absolute()
        self.auth_base_url = auth_base_url

    def authenticate(self, email: str, password: str) -> ProfileAuthSettings:
        with requests.Session() as s:
            user_info = get_payload(
                'retrieve user info',
                s.get(
                    url=str(self.auth_base_url / 'users'),
                    headers={'X-Api-Email': email, 'X-Api-Password': password}
                )
            )

            curr_org = user_info.get('currentOrganization')
            if curr_org is None:
                orgs: Optional[list[dict[Any, Any]]] = user_info.get('organizations')
                if orgs is None or len(orgs) == 0:
                    raise ApiErr(f'No organizations available for user {email}')

                curr_org = prompt_choose_dialog(
                    'Choose active organization:',
                    [(org, org['displayData']['name']) for org in orgs]
                )

                get_payload(
                    f'set {curr_org["displayData"]["name"]} as active organization',
                    s.put(url=str(self.auth_base_url / 'users' / 'organizations' / curr_org['id']))
                )

            api_token = get_payload(
                'generate API token',
                s.post(
                    url=str(self.auth_base_url / 'api-tokens'),
                    json={
                        'displayData': {
                            'name': f'apitoken-{email}-{datetime.datetime.now().timestamp()}',
                            'description': 'CLI generated token'
                        }
                    }
                )
            )['apiToken']

            # TODO unify w/ get_base_url (the issue is i'm using Session here)
            base_url = parse_url(
                get_payload(
                    'get base url for API calls',
                    s.get(url=str(self.auth_base_url / 'environments' / 'local-api'))
                )['dnsInfo']['name']
            )

            return ProfileAuthSettings(token=api_token, base_url=base_url)
