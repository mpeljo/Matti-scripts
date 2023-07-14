import base64

import requests


class GroundwaterDataLibraryAPI:
    def __init__(self, api_endpoint, api_key, client_id, client_secret, token_endpoint='https://auth.nonprod.my.ga.gov.au/oauth2/token'):
        self.token_endpoint = token_endpoint
        self.api_endpoint = api_endpoint

        self.api_key = api_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = api_endpoint + '/full'
        self.grant_type = 'client_credentials'

        self.access_token = self.setup_access_token()

    def setup_access_token(self):
        """Exchange client credential for access token from token endpoint"""

        response = requests.post(
            self.token_endpoint,
            data={'grant_type': self.grant_type, 'scope': self.scope},
            headers={'Authorization': f'Basic {self.get_credential()}'}
        ).json()

        return response['access_token']

    def get_credential(self):
        """Get base64 encoded client credentials"""

        return base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode('utf8')).decode('utf8')

    def call_get_api(self, path):
        """Call groundwater data library API using GET request"""

        return requests.get(
            self.api_endpoint + path,
            headers={
                'X-API-Key': self.api_key,
                'Authorization': self.access_token
            }
        ).json()

    def get_datastore_index(self):
        return self.call_get_api('/dataset/index')
