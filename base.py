

import requests


class API:
    BASE_URI = 'https://api.pipedrive.com/v1/'
    api_token = ''
    proxies = {}

    def authenticate(self, user, password, proxies={}):
        self.proxies = proxies
        session = requests.Session()
        response = session.post(
            self.BASE_URI + 'authorizations',
            data={'email': user, 'password': password},
            proxies=proxies,
        )
        resp_json = response.json()
        if resp_json['data']:
            self.api_token = resp_json['data'][0]['api_token']
            return True
        else:
            return False

    def request(self, method, path, params=None, data=None):
        if params is None:
            params = {}
        if data is None:
            data = {}
        params['api_token'] = self.api_token
        uri = self.BASE_URI + path

        session = requests.Session()
        methods = {
            'GET': session.get,
            'POST': session.post,
        }
        response = methods[method](
            uri,
            params=params, data=data, proxies=self.proxies,
        )
        resp_json = response.json()
        return resp_json

    def query(self, model):
        return Query(self, model)

    def write(self, model):
        return self.request('POST', model.__path__, data=model.attributes())


class Query:
    def __init__(self, api, Model):
        self.api = api
        self.Model = Model
        self.filter_id = ''

    def filter_by(self, filter_id):
        self.filter_id = filter_id
        return self

    def get(self, params):
        if self.filter_id:
            params.update({'filter_id': self.filter_id})
        response = self.api.request(
            method='GET',
            path=self.Model.__path__,
            params=params,
        )
        return response

    def get_one(self):
        return list(self.get_many('1'))[0]

    def get_many(self, limit, start=0):
        response = self.get(
            params={'start': start, 'limit': limit}
        )
        if not response['data']:
            return []

        for data in response['data']:
            model = self.Model(**data)
            yield model

    def get_all(self):
        start = 0
        limit = 50
        while True:
            response = self.get(params={'start': start, 'limit': limit})
            if not response['data']:
                break
            for data in response['data']:
                model = self.Model(**data)
                yield model

            if 'additional_data' not in response:
                break
            pagination = response['additional_data']['pagination']
            if pagination['more_items_in_collection']:
                start += 50
            else:
                break
