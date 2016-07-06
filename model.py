

from .util import urljoin


class Model:
    __attributes__ = {}
    __mapping__ = {
        'Activity': 'activities',
        'ActivityType': 'activityTypes',
        'Authorization': 'authorizations',
        'Currency': 'currencies',
        'Deal': 'deals',
        'File': 'files',
        'Filter': 'filters',
        'Note': 'notes',
        'Organization': 'organizations',
        'Person': 'persons',
        'Pipeline': 'pipelines',
        'Product': 'products',
        'SearchResult': 'searchResults',
        'Stage': 'stages',
        'User': 'users',
        'ActivityField': 'activityFields',
        'DealField': 'dealFields',
        'OrganizationField': 'organizationFields',
        'PersonField': 'personFields',
        'ProductField': 'productFields',
    }
    __custom_fields__ = {}

    def __init__(self, name, client, custom_fields={}):
        self.__name__ = name
        try:
            self.__path__ = self.__mapping__[name]
        except KeyError:
            raise TypeError('Model {} does not exist'.format(name))
        self.client = client
        self.__custom_fields__.update(custom_fields)

    def __call__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)
        self.__attributes__.update(data)
        return self

    def __getattr__(self, name):
        name = self.__custom_fields__.get(name, name)
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        name = self.__custom_fields__.get(name, name)
        if name not in ('client', ) or not name.startswith('__'):
            self.__attributes__[name] = value
        super().__setattr__(name, value)

    def __repr__(self):
        attributes = [
            '{}={}'.format(key, value)
            for key, value in self.__attributes__.items()
        ]
        values = '; '.join(attributes)
        return '<{name}({values})>'.format(name=self.__name__, values=values)

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
        if 'error' in response:
            print(response['error'], response['error_info'])
            return
        objects = response['data']
        if not objects:
            return []
        for data in objects:
            yield Model(self.__name__, self.client)(**data)

    def fetch_all(self, filter_id=None, start=0):
        current = start
        run = True
        while run:
            response = self.fetch_raw(filter_id, current, 50)
            if 'error' in response:
                print(response['error'], response['error_info'])
                break
            pagination = response['additional_data']['pagination']
            if pagination['more_items_in_collection']:
                current += 50
            else:
                run = False
            for data in response['data'] or []:
                yield Model(self.__name__, self.client)(**data)

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
