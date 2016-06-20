

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Model(Base):
    __aliases__ = {}

    def __init__(self, **kwargs):
        for key, value in list(kwargs.items()):
            try:
                alias = self.__aliases__[key]
            except KeyError:
                continue
            else:
                kwargs.pop(key)
                kwargs[alias] = value
        super().__init__(**kwargs)

    def __repr__(self):
        name = type(self).__name__
        attributes = self.ATTRIBUTES.keys()
        attributes = [
            '{}={}'.format(attr, getattr(self, attr)) for attr in attributes
        ]
        values = '; '.join(attributes)
        return '<{name}({values})>'.format(name=name, values=values)


class Organization(Model):
    __tablename__ = 'pipedrive_orgs'

    id = Column(Integer, primary_key=True)
    address = Column(String)
    address_admin_area_level_1 = Column(String)
    address_country = Column(String)
    address_formatted_address = Column(String)
    address_locality = Column(String)
    address_postal_code = Column(String)
    address_route = Column(String)
    address_street_number = Column(String)
    last_activity_date = Column(String)
    name = Column(String)
    owner_name = Column(String)


class OrganizationField(Model):
    PATH = 'organizationFields'
    ATTRIBUTES = {
        'id': None,
        'key': '',
        'name': '',
        'options': [],
    }


class Filter(Model):
    PATH = 'filters'
    ATTRIBUTES = {
        'id': None,
        'name': '',
        'type': '',
    }


class Deal(Model):
    PATH = 'deals'
    ATTRIBUTES = {
        'id': None,
    }


class User(Model):
    PATH = 'users'
    ATTRIBUTES = {
        'id': None,
    }


class Activity(Model):
    PATH = 'activitiies'
    ATTRIBUTES = {
        'id': None,
        'company_id': '',
        'user_id': '',
        'done': '',
        'type': '',
        'due_date': '',
        'add_time': '',
        'marked_as_done_time': '',
        'subject': '',
        'deal_id': '',
        'org_id': '',
        'person_id': '',
        'person_name': '',
        'org_name': '',
        'deal_title': '',
        'owner_name': '',
    }
