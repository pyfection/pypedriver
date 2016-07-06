# Pipedrive client for Python based apps (unofficial)


Pipedrive is a sales pipeline software that gets you organized. It's a powerful sales CRM with effortless sales pipeline management. See www.pipedrive.com for details.

This is an unofficial Pipedrive API wrapper-client for Python based apps, distributed by Matumaros freely under the MIT licence. It provides you with basic functionality for operating with objects such as Deals, Persons, Organizations, Products and much more, without having to worry about the underlying networking stack and actual HTTPS requests.
It is modelled in a similar way to the official client for [Node.js](https://github.com/pipedrive/client-nodejs)

# Install

Currently the easiest way to install it is to download it and move it into your python/Lib/sidte-packages folder. Easier ways will be added soon. You will also need the [requests](http://docs.python-requests.org/en/master/) package.

# Usage

With a pre-set API token:
```python
from pypedrive import Client
pipedrive = Client('YOUR_API_TOKEN_HERE')
```

# A simple "Hello world" that lists some deals

Here's a quick example that will list some deals from your Pipedrive account:

```python
from pypedrive import Client
pipedrive = Client('YOUR_API_TOKEN_HERE')

deals = pipedrive.Deals.fetch_all()
for deal in deals:
    print(deal.title, '(worth', deals.value, deals.currency + ')')
```

# Supported objects

 * Activities (Untested)
 * ActivityTypes (Untested)
 * Authorizations (Untested)
 * Currencies (Untested)
 * Deals (Untested)
 * DealFields (Untested)
 * Files (Untested)
 * Filters (Untested)
 * Notes (Untested)
 * Organizations
 * OrganizationFields
 * Persons
 * PersonFields (Untested)
 * Pipelines (Untested)
 * Products (Untested)
 * ProductFields (Untested)
 * SearchResults (Untested)
 * Stages (Untested)
 * Users (Untested)

# Authorization against email and password

### Client.authenticate(user='john@doe.com', password='example')
Fetches the possible API tokens for the given user against email and password. You can use the API tokens returned by this method to instantiate the API client by issuing ```pipedrive = Client('API_TOKEN_HERE')``` or directly enter email and password by issuing ```pipedrive = Client(user='john@doe.com', password='example')```.

# Supported operations for each object
> Note that the "Supported operations for object collections" part is omitted here, because it doesn't quite work the same way as for Node.js. By issuing ```pipedrive.{Object}```, you get an object of that type in return and can issue all following methods on it. You can also build chains with all but the ```fetch``` methods, because they return another object.

### {object}.fetch(filter_id=None, start=0, limit=50, sort=None)
Returns a maximum of ```limit``` objects as generator.

### {object}.fetch_raw(filter_id=None, start=0, limit=50, sort=None)
Returns the JSON response.

### {object}.fetch_all(filter_id=None, start=0, sort=None)
Returns as many objects as possible as generator.

### {object}.complete()
Uses the current object as filter and returns a new object or an error if it found multiple matches.

### {object}.save()
Update an object.

### {object}.remove()
Delete an object with a specifc ID.

### {object}.merge(with_id)
Merge two objects of the same kind. Returns ```error``` in case of an error to the callback. Merge is only supported for the following objects:
 * Persons
 * Organizations
 * Users

# Operations with nested objects

## Adding a product to a deal

Adding a product to a deal is not supported yet.

## Updating a deal product

Updating deal products is not supported yet.

## Delete a product from a deal

Deleting a product from a deal is not supported yet.

## Search for field value matches

Search for field value matches is not supported yet.

## Retrieve all records for a given object type:

You can request all entries for an valid object using `fetch_all(filter_id=None, start=0)`

```python
organizations = pipedrive.Organizations.fetch_all()
```

## Retrieve all records for a given object type which match a certain criteria:

You can request all entries for an valid object using a call on the Organization object.

```python
organizations = pipedrive.Organization(open_deals_count=0).fetch_all()
```

# Examples

## Get 15 first deals using the first deals filter

```python
from pypedrive import Client
pipedrive = Client(user='john@doe.com', password='example')

filter_list = list(pipedrive.Filter(type='deals').fetch_all())
if len(filter_list) > 0:
    deals = pipedrive.Deal.fetch(
        filter_id=filter_list[0].id,
        limit=15,
    )
    for deal in deals:
        print(deal.title, '(worth', deal.value, deal.currency + ')')
```

## Create copy of Organization with different owner_id

```python
from pypedrive import Client
pipedrive = Client(user='john@doe.com', password='example')

pipedrive.Organization(id=5).complete()(id=None, owner_id=6).save()
```

# API Documentation

The Pipedrive REST API documentation can be found at https://developers.pipedrive.com/v1

# Licence

This Pipedrive API client is distributed under the MIT licence.
