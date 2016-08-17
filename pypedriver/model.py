

from .util import urljoin, clean


class Model:
    MAPPING = {
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

    def __init__(self, name, client, custom_fields=None):
        """Model Manager

        This class manages the different models available on Pipedrive.

        Arguments:
            name {str} -- name of an Pipedrive object, e.g. "Organization"
            client {client.Client} -- instance of Client object

        Keyword Arguments:
            custom_fields {dict} -- {key: ModelField()} (default: {None})

        Raises:
            TypeError -- When argument 'name' not a valid model name
        """
        self.__name = name
        self.__custom_fields = custom_fields or {}
        try:
            self.__path = self.MAPPING[name]
        except KeyError:
            raise TypeError('Model {} does not exist'.format(name))
        self.__client = client
        self.__attributes = {}

    def __call__(self, **data):
        """Shortcut to update method

        This is a shortcut to Model.update.

        Arguments:
            **data {dict} -- {attribute_name: value}

        Returns:
            Model -- updated self
        """
        return self.update(**data)

    def __getattr__(self, name):
        name = self.get_field_key(name)
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if not name.startswith('_Model__'):
            name = self.get_field_key(name)
            self.__attributes[name] = value
        super().__setattr__(name, value)

    def __repr__(self):
        attributes = [
            '{}={}'.format(key, value)
            for key, value in self.__attributes.items()
        ]
        values = '; '.join(attributes)
        return '<{name}({values})>'.format(name=self.__name, values=values)

    def get_field_key(self, name):
        """Translate field key

        Translates the field key from how it is in the database to a human
        readable one.

        Arguments:
            name {str} -- field key

        Returns:
            str -- cleaned field key
        """
        fields = super().__getattribute__('_Model__custom_fields')
        for key, field in fields.items():
            if clean(field.name) == name:
                break
        else:
            key = None
        return key or name

    def update(self, **data):
        """Update own data

        Updates own data with the data given

        Arguments:
            **data {dict} -- {attribute_name: value}

        Returns:
            Model -- updated self
        """
        for key, value in data.items():
            key = self.get_field_key(key)
            try:
                options = self.__custom_fields[key].options
            except (AttributeError, KeyError):
                pass
            else:
                options = {int(o['id']): o['label'] for o in options}
                try:
                    value = options.get(int(value))
                except (ValueError, TypeError):
                    pass
            setattr(self, key, value)
        return self

    def fetch_raw(self, filter_id=None, start=0, limit=50, sort=None):
        """Fetch raw data

        Fetches raw object data in a dictionary format.
        It filters the results based on set attributes on this object.

        Keyword Arguments:
            filter_id {int} -- see: Filters (default: {None})
            start {int} -- id to start at (default: {0})
            limit {int} -- max of items to fetch (default: {50})
            sort {str} -- extra sorting string (default: {None})

        Returns:
            dict -- raw data

        Raises:
            ConnectionError -- When some error has occured while connecting
        """
        params = {'start': start, 'limit': limit}
        if filter_id:
            params.update({'filter_id': filter_id})
        if sort:
            params.update({'sort': sort})

        response = self.__client.request(
            method='GET',
            path=self.__path,
            params=params,
        )
        if 'error' in response:
            raise ConnectionError(response['error'] + response['error_info'])
        if not self.__attributes:
            return response
        attrs = self.__attributes.items()
        objects = response['data']
        data = []
        objects = list(objects)
        for obj in objects:
            items = obj.items()
            if all(item in items for item in attrs):
                data.append(obj)
        response['data'] = data
        return response

    def fetch(self, filter_id=None, start=0, limit=50, sort=None):
        """Fetch models

        Fetches models.
        It filters the results based on set attributes on this object.

        Keyword Arguments:
            filter_id {int} -- see: Filters (default: {None})
            start {int} -- id to start at (default: {0})
            limit {int} -- max of items to fetch (default: {50})
            sort {str} -- extra sorting string (default: {None})

        Yields:
            Model -- model that corresponds to filters and set attributes
        """
        response = self.fetch_raw(filter_id, start, limit, sort)
        objects = response['data']
        if not objects:
            return []
        for data in objects:
            yield getattr(self.__client, self.__name)(**data)

    def fetch_all(self, filter_id=None, start=0, limit=None):
        """Fetch all models

        Fetches all models.
        It filters the results based on set attributes on this object.

        Keyword Arguments:
            filter_id {int} -- see: Filters (default: {None})
            start {int} -- id to start at (default: {0})
            limit {int} -- maximum of returned objects (default: {None})

        Yields:
            Model -- model that corresponds to filters and set attributes
        """
        current = start
        yielded = 0
        run = True
        while run:
            response = self.fetch_raw(filter_id, current, 50)
            pagination = response['additional_data']['pagination']
            if pagination['more_items_in_collection']:
                current += 50
            else:
                run = False
            for data in response['data'] or []:
                if limit and yielded >= limit:
                    break
                yielded += 1
                yield getattr(self.__client, self.__name)(**data)
            else:
                continue
            break

    def complete(self):
        """Complete self

        Tries to complete itself based on set attributes.

        Returns:
            Model -- self

        Raises:
            ValueError -- When set attributes are not precise enough to
                          match exactly one object
        """
        models = list(self.fetch_all(limit=2))
        if not models:
            raise ValueError(
                'No model exists based on set attributes, got no result.'
            )
        elif len(models) > 1:
            raise ValueError(
                'Model is too ambiguous to complete, got too many results.'
            )
        else:
            model = models[0]
        return model

    def save(self):
        """Add/Update on REST

        Sends current data to the Pipedrive REST API to be added.
        If the current model has an id, then it will be updated instead.

        Returns:
            Model -- self
        """
        if 'id' not in self.__attributes or self.id is None:
            method = 'POST'
            path = self.__path
        else:
            method = 'PUT'
            path = urljoin(self.__path, str(self.id))
        response = self.__client.request(
            method=method,
            path=path,
            data=self.__attributes,
        )
        if 'error' in response:
            raise ConnectionError(response['error'])
        return self

    def remove(self):
        """Remove on REST

        Marks the current model as removed in the Pipedrive REST API.

        Returns:
            Model -- self

        Raises:
            AttributeError -- When id is not set
        """
        try:
            id = self.id
        except AttributeError:
            raise AttributeError('Requires the attribute "id" to be set')
        response = self.__client.request(
            method='DELETE',
            path=urljoin(self.__path, str(id)),
        )
        if 'error' in response:
            raise ConnectionError(response['error'])
        return self

    def merge(self, with_id):
        """Merge on REST

        Merges the current model with another one in the Pipedrive REST API.

        Arguments:
            with_id {int} -- id of object to merge with

        Returns:
            Model -- self

        Raises:
            AttributeError -- When id is not set
        """
        try:
            id = self.id
        except AttributeError:
            raise AttributeError('Requires the attribute "id" to be set')
        response = self.__client.request(
            method='PUT',
            path=urljoin(self.__path, str(id), 'merge'),
            data={'merge_with_id': with_id},
        )
        if 'error' in response:
            raise ConnectionError(response['error'])
        return self
