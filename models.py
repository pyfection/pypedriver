

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Model(Base):
    __abstract__ = True
    __aliases__ = {}

    id = Column(Integer, primary_key=True)

    def __init__(self, **kwargs):
        for key, value in list(kwargs.items()):
            try:
                alias = self.__aliases__[key]
            except KeyError:
                continue
            else:
                kwargs.pop(key)
                kwargs[alias] = value
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        name = type(self).__name__
        attributes = self.__table__.columns._data.keys()
        attributes = [
            '{}={}'.format(
                attr,
                getattr(self, attr),
            ) for attr in attributes
        ]
        values = '; '.join(attributes)
        return '<{name}({values})>'.format(name=name, values=values)


class Organization(Model):
    __tablename__ = 'pipedrive_orgs'
    __path__ = 'organizations'

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


# class OrganizationField(Base, Model):
#     __tablename__ = 'organization_fields'

#     PATH = 'organizationFields'
#     ATTRIBUTES = {
#         'id': None,
#         'key': '',
#         'name': '',
#         'options': [],
#     }


# class Filter(Base, Model):
#     __tablename__ = 'filters'

#     PATH = 'filters'
#     ATTRIBUTES = {
#         'id': None,
#         'name': '',
#         'type': '',
#     }


# class Deal(Base, Model):
#     __tablename__ = 'deals'

#     PATH = 'deals'
#     ATTRIBUTES = {
#         'id': None,
#     }


# class User(Base, Model):
#     __tablename__ = 'users'

#     PATH = 'users'
#     ATTRIBUTES = {
#         'id': None,
#     }


# class Activity(Base, Model):
#     __tablename__ = 'activities'

#     PATH = 'activities'
#     ATTRIBUTES = {
#         'id': None,
#         'company_id': '',
#         'user_id': '',
#         'done': '',
#         'type': '',
#         'due_date': '',
#         'add_time': '',
#         'marked_as_done_time': '',
#         'subject': '',
#         'deal_id': '',
#         'org_id': '',
#         'person_id': '',
#         'person_name': '',
#         'org_name': '',
#         'deal_title': '',
#         'owner_name': '',
#     }
