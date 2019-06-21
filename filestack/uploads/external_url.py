import requests

from filestack import config


def upload_external_url(url, apikey, store_params=None, security=None):
    # TODO handle store_params
    if security is not None:
        request_url = '{}/{}/{}/store/{}'.format(
            config.CDN_URL, apikey, security.as_url_string(), url
        )
    else:
        request_url = '{}/{}/store/{}'.format(config.CDN_URL, apikey, url)

    response = requests.post(request_url)

    if not response.ok:
        raise Exception(response.text)

    return response.json()['handle']
