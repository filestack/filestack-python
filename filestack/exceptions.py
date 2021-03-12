class FilestackHTTPError(Exception):
    """
    Custom HTTPError instead of requests.exceptions.HTTPError to add response body.

    References:
        - https://github.com/psf/requests/pull/4234
    """
