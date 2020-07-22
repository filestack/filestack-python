import base64
from unittest.mock import patch

import pytest

from tests.helpers import DummyHttpResponse
from filestack import config
from filestack.models import Security
from filestack.uploads.external_url import upload_external_url

url = 'http://image.url'
encoded_url = 'b64://{}'.format(base64.urlsafe_b64encode(url.encode()).decode())
apikey = 'TESTAPIKEY'


@patch('filestack.uploads.external_url.requests.get')
def test_upload(post_mock):
    post_mock.return_value = DummyHttpResponse(json_dict={'handle': 'newHandle'})

    handle = upload_external_url(url, apikey)
    assert handle == 'newHandle'
    post_mock.assert_called_once_with('{}/{}/store/{}'.format(config.CDN_URL, apikey, encoded_url))


@pytest.mark.parametrize('store_params, expected_store_task', [
    [{'location': 'S3'}, 'store=location:s3'],
    [{'path': 'store/path/image.jpg'}, 'store=path:"store/path/image.jpg"'],
    [{'base64decode': True, 'access': 'public'}, 'store=access:public,base64decode:true'],
    [
        {'workflows': ['uuid-1', 'uuid-2'], 'container': 'bucket-name'},
        'store=container:bucket-name,workflows:["uuid-1","uuid-2"]'
    ],
])
@patch('filestack.uploads.external_url.requests.get')
def test_upload_with_store_params(post_mock, store_params, expected_store_task):
    post_mock.return_value = DummyHttpResponse(json_dict={'handle': 'newHandle'})

    handle = upload_external_url(url, apikey, store_params=store_params)
    assert handle == 'newHandle'
    post_args, _ = post_mock.call_args
    req_url = post_args[0]
    assert expected_store_task in req_url


@patch('filestack.uploads.external_url.requests.get')
def test_upload_with_security(post_mock):
    post_mock.return_value = DummyHttpResponse(json_dict={'handle': 'newHandle'})
    security = Security({'expiry': 123123123123, 'call': ['write']}, 'SECRET')
    handle = upload_external_url(url, apikey, security=security)
    assert handle == 'newHandle'
    expected_url = '{}/{}/store/{}/{}'.format(
        config.CDN_URL, apikey, security.as_url_string(), encoded_url
    )
    post_mock.assert_called_once_with(expected_url)


@patch('filestack.uploads.external_url.requests.get')
def test_upload_exception(post_mock):
    error_message = 'Oops!'
    post_mock.side_effect = Exception(error_message)

    with pytest.raises(Exception, match=error_message):
        upload_external_url(url, apikey)
