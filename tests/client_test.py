from unittest.mock import patch, mock_open
from collections import defaultdict

import pytest
from trafaret import DataError
from httmock import urlmatch, HTTMock, response

import filestack.models
from filestack import Client, Filelink, Transformation, Security
from tests.helpers import DummyHttpResponse


APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'


@pytest.fixture
def client():
    return Client(APIKEY)


def test_api_set(client):
    assert client.apikey == APIKEY


def test_wrong_storage():
    kwargs = {'apikey': APIKEY, 'storage': 'googlecloud'}
    pytest.raises(DataError, Client, **kwargs)


def test_store_external_url(client):
    @urlmatch(netloc=r'cdn.filestackcontent\.com', method='post', scheme='https')
    def api_store(url, request):
        return response(200, {'handle': HANDLE})

    with HTTMock(api_store):
        filelink = client.upload_url(url="someurl", store_params={'filename': 'something.jpg'})

    assert isinstance(filelink, Filelink)
    assert filelink.handle == HANDLE


@patch('filestack.models.client.multipart_upload')
def test_store_filepath(upload_mock, client):
    upload_mock.return_value = {'handle': HANDLE}
    filelink = client.upload(filepath='path/to/image.jpg')

    assert isinstance(filelink, Filelink)
    assert filelink.handle == HANDLE
    upload_mock.assert_called_once_with('APIKEY', 'path/to/image.jpg', None, 'S3', params=None, security=None)


@patch('filestack.models.client.multipart_upload')
@patch('filestack.models.client.upload_external_url')
def test_security_inheritance(upload_external_mock, multipart_mock):
    upload_external_mock.return_value = 'URL_HANDLE'
    multipart_mock.return_value = {'handle': 'FILE_HANDLE'}

    policy = {'expiry': 1900}
    cli = Client(APIKEY, security=Security(policy, 'SECRET'))

    flink_from_url = cli.upload_url('https://just.some/url')
    assert flink_from_url.handle == 'URL_HANDLE'
    assert flink_from_url.security.policy == policy

    flink = cli.upload(filepath='/dummy/path')
    assert flink.handle == 'FILE_HANDLE'
    assert flink.security.policy == policy


def test_url_screenshot(client):
    external_url = 'https//www.someexternalurl'
    transform = client.urlscreenshot(external_url)
    assert isinstance(transform, filestack.models.Transformation)
    assert transform.apikey == APIKEY


def test_transform_external(client):
    new_transform = client.transform_external('SOMEURL')
    assert isinstance(new_transform, Transformation)


def test_zip(client):
    @urlmatch(netloc=r'cdn.filestackcontent\.com', method='get', scheme='https')
    def api_zip(url, request):
        return response(200, b'zip-bytes')

    m = mock_open()
    with patch('filestack.models.client.open', m):
        with HTTMock(api_zip):
            zip_size = client.zip('test.zip', ['handle1', 'handle2'])

    assert zip_size == 9
    m().write.assert_called_once_with(b'zip-bytes')


@patch('requests.put')
@patch('requests.post')
def test_upload_multipart_workflows(post_mock, put_mock, client):

    workflow_ids = ['workflow-id-1', 'workflow-id-2']
    store_params = {'workflows': workflow_ids}
    put_mock.return_value = DummyHttpResponse(headers={'ETag': 'some_tag'})
    post_mock.side_effect = [
        DummyHttpResponse(json_dict=defaultdict(str)),
        DummyHttpResponse(json_dict=defaultdict(str)),
        DummyHttpResponse(json_dict={'handle': 'new_handle'})
    ]

    new_filelink = client.upload(filepath='tests/data/bird.jpg', store_params=store_params)

    post_args, post_kwargs = post_mock.call_args
    assert post_kwargs['json']['store']['workflows'] == workflow_ids
    assert new_filelink.handle == 'new_handle'
