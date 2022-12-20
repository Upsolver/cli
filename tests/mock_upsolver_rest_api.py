from pathlib import Path
from typing import Optional

from requests_mock import Mocker as RequestsMocker

DEFAULT_ORG = 'testorg'
DEFAULT_BASE_URL = 'localhost'
DEFAULT_TOKEN = 'token123'


class MockUpsolverRestApi(object):
    """
    Simulates Upsolver's REST API. We're using the 'requests' package to issue all http requests
    and using requests-mock package we can mock responses.
    """

    _users_resp = {
        'currentOrganization': DEFAULT_ORG,
        'organizations': [
            {
                'displayData': {
                    'name': DEFAULT_ORG
                }
            }
        ]
    }

    def __init__(self, requests_mock: RequestsMocker, conf_path: Optional[Path] = None) -> None:
        self.catalogs: list = []

        if conf_path is not None:
            basic_config = f'''[profile]
            token = {DEFAULT_TOKEN}
            base_url = http://{MockUpsolverRestApi}
            output = JSON
            '''

            with open(conf_path, 'w') as conf_f:
                conf_f.write(basic_config)

        self.mock = requests_mock
        # Response for invalid credentials (add_user adds valid responses with correct creds)
        self.mock.get(
            '/users',
            status_code=403,
            headers={'X-Api-RequestId': 'reqid123'},
            text='null'
        )

        # Used to generate API token
        self.mock.post(
            '/api-tokens',
            json={'apiToken': DEFAULT_TOKEN}
        )

        # allow "login" via token
        self.mock.get(
            '/users',
            request_headers={
                'Authorization': DEFAULT_TOKEN
            },
            json=self._users_resp
        )

        self.mock.get(
            '/jobs',
            request_headers={
                'Authorization': DEFAULT_TOKEN
            },
            json={
                'jobs': [
                    {
                        'connector': 'S3',
                        'name': 'extract data from tutorials',
                        'description': '',
                        'status': 'Running',
                        'delay': 0,
                        'errorsLastDay': 22109,
                        'creationTime': '2022-03-23T15:05:02.921336Z',
                        'createdBy': 'xx', 'createdByName': 'test',
                        'createdByEmail': 'something@email.com',
                        'modifiedTime': '2022-03-23T15:05:02.926602Z',
                        'modifiedBy': 'modifyby',
                        'modifiedByName': 'mofidy by',
                        'modifiedByEmail': 'modify@email.com',
                        'wizards': []
                    },
                ]
            }
        )

        # catalogs api response
        self.mock.get('/connections', json=[])

        # query api (execute)
        self.mock.post('/query', json={})

        self.set_base_url(DEFAULT_BASE_URL)

    def set_base_url(self, base_url: Optional[str]) -> None:
        # Used to retrieve base url for further requests (aka "base url")
        j = {}
        if base_url is not None:
            j = {
                'dnsInfo': {
                    'name': base_url
                }
            }

        self.mock.get('/environments/local-api', json=j)

    def add_user(self, email: str, password: str) -> None:
        """
        Ensures that subsequent requests with provided credentials will be recognized as a valid
        user.
        """
        # "Login" method
        self.mock.get(
            '/users',
            request_headers={
                'X-Api-Email': email,
                'X-Api-Password': password
            },
            json=self._users_resp
        )
