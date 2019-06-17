from unittest.mock import patch
from base64 import b64encode
from collections import defaultdict

import pytest
from trafaret import DataError
from httmock import urlmatch, HTTMock, response

import filestack.models
from filestack import Client, Filelink, Transform
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


@patch('filestack.models.filestack_client.upload_utils.multipart_upload')
def test_store_filepath(upload_mock, client):
    upload_mock.return_value = {'handle': HANDLE}
    filelink = client.upload(filepath='tests/data/bird.jpg')

    assert isinstance(filelink, Filelink)
    assert filelink.handle == HANDLE
    upload_mock.assert_called_once_with(
        'APIKEY', 'tests/data/bird.jpg', 'S3', params=None, security=None
    )


def test_url_screenshot(client):
    external_url = 'https//www.someexternalurl'
    transform = client.urlscreenshot(external_url)
    assert isinstance(transform, filestack.models.Transform)
    assert transform.apikey == APIKEY


def test_transform_external(client):
    new_transform = client.transform_external('SOMEURL')
    assert isinstance(new_transform, Transform)


def test_zip(client):
    @urlmatch(netloc=r'cdn.filestackcontent\.com', method='get', scheme='https')
    def api_zip(url, request):
        with open('tests/data/bird.jpg', 'rb') as f:
            return response(200, b64encode(f.read()))

    with HTTMock(api_zip):
        zip_response = client.zip('test.zip', 'tests/data/bird.jpg')

        assert zip_response.status_code == 200


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


def test_webhooks_signature():
    resp = Client.verify_webhook_signature(100, b'{"test": "content"}', {'test': 'headers'})
    assert resp == {'error': 'Missing secret or secret is not a string', 'valid': True}

    resp = Client.verify_webhook_signature('a', b'{"test": "content"}')
    assert resp == {'error': 'Missing headers or headers are not a dict', 'valid': True}

    resp = Client.verify_webhook_signature('a', {"test": "content"}, {'header': 'header'})
    assert resp == {'error': 'Missing content or content is not string/bytes type', 'valid': True}

    resp = Client.verify_webhook_signature('a', '{"test": "content"}', {'fs-timestamp': 'header'})
    assert resp == {'error': 'Missing `Signature` value in provided headers', 'valid': True}

    resp = Client.verify_webhook_signature('a', '{"test": "content"}', {'header': 'header'})
    assert resp == {'error': 'Missing `Timestamp` value in provided headers', 'valid': True}

    content = '{"timestamp": 1558123673, "id": 1000, "text": {"filename": "filename.jpg", "type": "image/jpeg", "container": "your-bucket", "client": "Computer", "status": "Stored", "url": "https://cdn.filestackcontent.com/Handle1Handle1Handle1", "key": "kGaeljnga9wkysK6Z_filename.jpg", "test": [], "test1": {}, "size": 100000}, "action": "fp.upload"}'
    secret = 'SecretSecretSecretAA'

    headers = {
        'FS-Signature': '4b058e4065206cfc13d57a8480cbd5915f9d2ed4e3fa4179e7fe82c6e58dc6d5',
        'FS-Timestamp': '1558384364'
    }
    resp = Client.verify_webhook_signature(secret, content, headers)
    assert resp == {'error': None, 'valid': True}

    headers['FS-Signature'] = '4450cd49aad51b689cbde0b7d462ae5fdd7e4e5bd972cc3e7fd6373c442871c7'
    resp = Client.verify_webhook_signature(secret, content, headers)
    assert resp == {'error': None, 'valid': False}
