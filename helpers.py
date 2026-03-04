"""General helper utilities for the JSON server"""

from urllib.parse import urlparse


def is_valid_url(url_string):
    """Returns True if url_string is a valid http or https URL"""
    parsed = urlparse(url_string)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)
