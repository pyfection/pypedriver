

import re


def urljoin(*pieces):
    """Join a URL

    Joins the pieces together to an URL.
    Cannot be replaced by urllib.parse.urljoin,
    because that doesn't join parts of a path and
    doesn't allow for multiple pieces to be joined.

    Arguments:
        *pieces {str} -- pieces of URL
    """
    return '/'.join(s.strip('/') for s in pieces)


def clean(string):
    """Clean string

    Cleans a string to be a valid Python variable name.
    It replaces all invalid characters with an underscore.

    Arguments:
        string {str} -- string to be formatted

    Returns:
        str -- formatted string
    """
    string = re.sub('\W|^(?=\d)', '_', string).lower()
    return string
