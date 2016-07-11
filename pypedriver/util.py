

import re


def urljoin(*pieces):
    """Join a internet URL

    Joins the pieces together to an URL.

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
