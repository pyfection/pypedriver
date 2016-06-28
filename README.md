# pypedrive
Python API for the PipeDrive API.

This is an API completely written in Python to access the PipeDrive API (v1) more easily over Python.
The only dependencies are the request module and SQLAlchemy.

---
### Example on How to Start
First of all we need to import the API and the models we will use.
```python
from pypedrive import API
from pypedrive.models import Organization
```
Then we need to authenticate.
```python
api = API()
success = api.authenticate(
    username='testname@testcompany.com',
    password='mypassword123',
    proxies={'https': '1.2.3.4:4567'},  # This is optional
)
print('Successful authenticated' if success else 'Authentication failed')
```
The next step is to retrieve information, which uses "GET".
```python
query = api.query(Organization)
query.filter_by(1)
orgs = query.get_all()
```
The first part gets us a query on which we can operate. Important to note is that we have not made a request to PipeDrive yet.
In the second step we tell the query to use the filter which is specified in PipeDrive with the ID "1".
In the third step we get a generator. We still did not make any request to the server, that happens when you iterate over "orgs".
```python
for org in orgs:
    print(org)
```
> Although pypedrive uses SQLAlchemy for the models, a database is not required.
> However if you wish to store the models, then you can use them just like any other SQLAlchemy model.
