from filestack.config import HEADERS

import requests


def get_url(base, handle=None, path=None, security=None):
    url_components = [base]

    if path:
        url_components.append(path)

    if security:
        url_components.append('security=policy:{policy},signature:{signature}'.format(policy=security['policy'],
                                                                                      signature=security['signature']))
    if handle:
        url_components.append(handle)

    return '/'.join(url_components)


def make_call(base, action, handle=None, path=None, params=None, data=None, files=None, security=None, transform_url=None):
    request_func = getattr(requests, action)

    if transform_url:
        return request_func(transform_url, params=params, headers=HEADERS, data=data, files=files)

    if security:
        url = get_url(base, path=path, handle=handle, security=security)
    else:
        url = get_url(base, path=path, handle=handle)

    return request_func(url, params=params, headers=HEADERS, data=data, files=files)
