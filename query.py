

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
