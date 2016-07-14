# -*- coding: utf-8 -*-
"""Pipedrive API Python Client.

pypedriver lets you interact with the Pipedrive API, much like the official
client for Node.js.

Example:
    Getting Organizations with postal code '12345' and update them::

        from pypedriver import Client
        pipedrive = Client(token='8727f6369aaf83ca15026747af8c7f196ce3f0ad')
        orgs = pipedrive.Organization(address_postal_code='12345').fetch_all()
        for org in orgs:
            org.address_postal_code='54321'
            org.save()

See https://github.com/matumaros/pypedriver for more information.

"""

from .client import Client


__author__ = "Matthias Schreiber"
__license__ = "MIT"
__version__ = "1.2"
__maintainer__ = "Matthias Schreiber"
__email__ = "mat@boar.bar"
__status__ = "Beta"
