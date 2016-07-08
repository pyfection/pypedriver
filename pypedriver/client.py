

import requests

from .model import Model
from .util import urljoin


BASE_URI = 'https://api.pipedrive.com/v1/'


class Client:
    api_token = ''
    proxies = {}
    custom_field_models = {
        'Activity': 'ActivityField',
        'Deal': 'DealField',
        'Organization': 'OrganizationField',
        'Person': 'PersonField',
        'Product': 'ProductField',
    }
    custom_fields = {}

    def __init__(self, token=None, user=None, password=None, proxies={}):
        try:
            assert token or user and password
        except AssertionError:
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

        for model_name, field_model in self.custom_field_models.items():
            model = Model(field_model, self)
            models = model.fetch_all()
            fields = {}
            for model in models:
                if len(model.key) == 40:
                    fields[model.key] = model
            self.custom_fields[model_name] = fields

    def __getattr__(self, name):
        return Model(name, self, self.custom_fields[name])

    @staticmethod
    def authenticate(user, password, proxies={}):
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
