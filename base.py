

import itertools

import requests


class Client:
    BASE_URI = 'https://api.pipedrive.com/v1/'
    api_token = ''
    proxies = {}

    def __init__(self, token=None, user=None, password=None, proxies=None):
        try:
            assert token or user and password
        except AssertionError:
            raise TypeError('Client expects token or user and password')

        if proxies:
            self.proxies = proxies
        if token:
            self.api_token = token
        else:
            token = self.authenticate(user, password)
            if token:
                self.api_token = token
            else:
                raise TypeError('Could not authenticate')

    def __getattr__(self, name):
        mapping = {
            'Organization': 'organizations',
            'Person': 'persons',
        }
        try:
            path = mapping[name]
        except KeyError:
            raise TypeError('Model {} does not exist'.format(name))
        return Model(path, self)

    def authenticate(self, user, password):
        session = requests.Session()
        response = session.post(
            self.BASE_URI + 'authorizations',
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
        uri = urljoin(self.BASE_URI, path)

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

    def get(self, Model, id):
        response = self.request(
            method='GET',
            path=Model.__path__ + '/' + str(id),
        )
        return Model(**response['data'])

    def query(self, Model):
        return Query(self, Model)

    def update(self, model, id=None):
        path = model.__path__ + '/' + str(id or model.id)
        return self.request('PUT', path, data=model.attributes())

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


class Model:
    def __init__(self, path, client):
        self.__path__ = path
        self.client = client
        self.__attributes__ = {}

    def __call__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)
        self.__attributes__.update(data)
        return self

    def __setattr__(self, name, value):
        self.__attributes__[name] = value
        super().__setattr__(self, name, value)

    def fetch_raw(self, filter_id=None, start=0, limit=50, sort=None):
        params = {'start': start, 'limit': limit}
        if filter_id:
            params.update({'filter_id': filter_id})
        if sort:
            params.update({'sort': sort})

        return self.client.request(
            method='GET',
            path=self.__path__,
            params=params,
        )

    def fetch(self, filter_id=None, start=0, limit=50, sort=None):
        response = self.fetch_raw(filter_id, start, limit, sort)
        objects = response['data']
        if not objects:
            return []
        for data in objects:
            yield Model(self.__path__, self.client)(**data)

    def fetch_all(self, filter_id=None, start=0):
        current = start
        run = True
        while run:
            response = self.fetch_raw(filter_id, current, 50)
            pagination = response['additional_data']['pagination']
            if pagination['more_items_in_collection']:
                current += 50
            else:
                run = False
            for data in response['data']:
                yield Model(self.__path__, self.client)(**data)

    def complete(self):
        models = list(self.fetch(limit=2))
        if len(models) > 1:
            raise ValueError(
                'Model is too ambiguous to complete, got too many results'
            )
        else:
            model = models[0]
        return model

    def save(self):
        if 'id' in self.__attributes__:
            method = 'POST'
            path = self.__path__
        else:
            method = 'PUT'
            path = urljoin(self.__path__, str(self.id))
        self.client.request(
            method=method,
            path=path,
            params=self.__attributes__,
        )
        return self

    def remove(self):
        try:
            id = self.id
        except AttributeError:
            raise AttributeError('Requires the attribute "id" to be set')
        self.client.request(
            method='DELETE',
            path=urljoin(self.__path__, str(id)),
        )
        return self

    def merge(self, with_id):
        try:
            id = self.id
        except AttributeError:
            raise AttributeError('Requires the attribute "id" to be set')
        self.client.request(
            method='PUT',
            path=urljoin(self.__path__, str(id), 'merge'),
            params={'merge_with_id': with_id},
        )
        return self


def urljoin(*pieces):
    return '/'.join(s.strip('/') for s in pieces)
