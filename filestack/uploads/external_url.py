import base64
from collections import OrderedDict

from filestack.utils import requests

from filestack import config


def build_store_task(store_params):
    if not store_params:
        return 'store'

    task_args = []
    store_params = OrderedDict(sorted(store_params.items(), key=lambda t: t[0]))
    for key, value in store_params.items():
        if key in ('filename', 'location', 'path', 'container', 'region', 'access', 'base64decode', 'workflows'):
            if key == 'workflows':
                value = '[{}]'.format(','.join('"{}"'.format(item) for item in value))
            if key == 'path':
                value = '"{}"'.format(value)
            task_args.append('{}:{}'.format(key, str(value).lower()))

    return 'store={}'.format(','.join(task_args))


def upload_external_url(url, apikey, store_params=None, security=None):
    store_task = build_store_task(store_params or {})
    encoded_url = 'b64://{}'.format(base64.urlsafe_b64encode(url.encode()).decode())
    url_elements = [config.CDN_URL, apikey, store_task, encoded_url]

    if security is not None:
        url_elements.insert(3, security.as_url_string())

    # TODO: use processing endpoint and "store" task for uploading external urls
    response = requests.get('/'.join(url_elements))
    return response.json()['handle']
