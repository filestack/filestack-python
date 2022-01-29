import re
from unittest.mock import patch, mock_open

import pytest
import responses
from trafaret import DataError

import filestack.models
from filestack import Client, Filelink, Transformation, Security


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


@responses.activate
def test_store_external_url(client):
    responses.add(
        responses.POST, 'https://cdn.filestackcontent.com/process', json={'handle': HANDLE}
    )
    filelink = client.upload_url(url='http://a.bc')

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
    upload_external_mock.return_value = {'handle': 'URL_HANDLE'}
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


@responses.activate
def test_zip(client):
    responses.add(
        responses.GET, re.compile('https://cdn.filestackcontent.com/APIKEY/zip*'),
        body=b'zip-bytes'
    )
    m = mock_open()
    with patch('filestack.models.client.open', m):
        zip_size = client.zip('test.zip', ['handle1', 'handle2'])

    assert zip_size == 9
    m().write.assert_called_once_with(b'zip-bytes')
