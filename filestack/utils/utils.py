from filestack.config import CDN_URL, PROCESS_URL, HEADERS

import requests

def get_security_path(url, security):
    return '{url_path}?signature={signature}&policy={policy}'.format(
        url_path=url, policy=security['policy'].decode('utf-8'), signature=security['signature']
    )


def get_url(base, handle=None, path=None, security=None):
    url_components = [base]

    if path:
        url_components.append(path)

    if handle:
        url_components.append(handle)

    url_path =  '/'.join(url_components)

    if security:
        return get_security_path(url_path, security)

    return url_path


def get_transform_url(tasks, external_url=None, handle=None, security=None, apikey=None, video=False):
    url_components = [(PROCESS_URL if video else CDN_URL)]
    if external_url:
        url_components.append(apikey)

    if 'debug' in tasks:
        index = tasks.index('debug')
        tasks.pop(index)
        tasks.insert(0, 'debug')

    url_components.append('/'.join(tasks))
    
    if security:
        url_components.append('security=policy:{},signature:{}'.format(
            security['policy'].decode('utf-8'), security['signature']))
    
    url_components.append(handle or external_url)

    url_path = '/'.join(url_components)

    return url_path


def make_call(base, action, handle=None, path=None, params=None, data=None, files=None, security=None, transform_url=None):
    request_func = getattr(requests, action)
    if transform_url:
        return request_func(transform_url, params=params, headers=HEADERS, data=data, files=files)

    url = get_url(base, path=path, handle=handle, security=security)
    response = request_func(url, params=params, headers=HEADERS, data=data, files=files)

    if not response.ok:
        raise Exception(response.text)
        
    return response 


def return_transform_task(transformation, params):
    transform_tasks = []

    for key, value in params.items():

        if isinstance(value, list):
            value = str(value).replace("'", "").replace('"', '').replace(" ", "")
        if isinstance(value, bool):
            value = str(value).lower()

        transform_tasks.append('{}:{}'.format(key, value))

    transform_tasks = sorted(transform_tasks)

    if len(transform_tasks) > 0:
        transformation_url = '{}={}'.format(transformation, ','.join(transform_tasks))
    else:
        transformation_url = transformation

    return transformation_url
