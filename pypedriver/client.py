

import requests

from .model import Model
from .util import urljoin


BASE_URI = 'https://api.pipedrive.com/v1/'


class Client:
    api_token = ''
    proxies = {}
    CUSTOM_FIELD_MODELS = {
        'Activity': 'ActivityField',
        'Deal': 'DealField',
        'Organization': 'OrganizationField',
        'Person': 'PersonField',
        'Product': 'ProductField',
    }
    custom_fields = {}

    def __init__(self, token=None, user=None, password=None, proxies={}):
        """Pipedrive Client

        The client for Pipedrive which handles all requests.

        Keyword Arguments:
            token {str} -- 40 digit hex code (default: {None})
            user {str} -- user email address (default: {None})
            password {str} -- user password (default: {None})
            proxies {dict} -- optional proxies to use (default: {{}})

        Raises:
            TypeError -- When token or user and password are not given
            TypeError -- When authentication failed
        """
        if not (token or user and password):
            raise TypeError('Client expects token or user and password')

        if proxies:
            self.proxies = proxies
        if token:
            self.api_token = token
        else:
            token = self.authenticate(user, password, proxies)
            if token:
                self.api_token = token
            else:
                raise TypeError('Could not authenticate')

        for model_name, field_model in self.CUSTOM_FIELD_MODELS.items():
            model = Model(field_model, self)
            models = model.fetch_all()
            fields = {}
            for model in models:
                if len(model.key) == 40:
                    fields[model.key] = model
            self.custom_fields[model_name] = fields

    def __getattr__(self, name):
        if name[0].isupper():
            return Model(name, self, self.custom_fields.get(name, {}))
        else:
            return super().__getattribute__(name)

    @staticmethod
    def authenticate(user, password, proxies={}):
        """Authentication to server

        Checks if user and password are valid and returns token if so.

        Arguments:
            user {str} -- user email address
            password {str} -- user password

        Keyword Arguments:
            proxies {dict} -- optional proxies to use (default: {{}})

        Returns:
            str or None -- Token if successful else None
        """
        session = requests.Session()
        response = session.post(
            urljoin(BASE_URI, 'authorizations'),
            data={'email': user, 'password': password},
            proxies=proxies,
        )
        resp_json = response.json()
        if resp_json['data']:
            return resp_json['data'][0]['api_token']
        else:
            return None

    def request(self, method, path, params=None, data=None):
        """Generic request

        Sends a generic request to the server and returns the response.

        Arguments:
            method {str} -- Any of the supported methods
                            ('GET', 'POST', 'PUT', 'DELETE')
            path {str} -- relative path of request

        Keyword Arguments:
            params {dict} -- parameters to send (default: {None})
            data {dict} -- data to send (default: {None})

        Returns:
            dict -- response of server
        """
        if params is None:
            params = {}
        if data is None:
            data = {}
        params['api_token'] = self.api_token
        uri = urljoin(BASE_URI, path)

        session = requests.Session()
        methods = {
            'GET': session.get,
            'POST': session.post,
            'PUT': session.put,
            'DELETE': session.delete,
        }
        response = methods[method](
            uri,
            params=params, data=data, proxies=self.proxies,
        )
        resp_json = response.json()
        return resp_json
