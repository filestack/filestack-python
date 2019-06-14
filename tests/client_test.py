import filestack.models
import pytest

from mock import patch
from base64 import b64encode
from filestack import Client, Filelink, Transform
from httmock import urlmatch, HTTMock, response
from trafaret import DataError
from collections import defaultdict


APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'


class MockResponse:
    ok = True
    headers = {'ETag': 'some_tag'}

    def __init__(self, json=None):
        self.json_data = defaultdict(str) if json is None else json

    def json(self):
        return self.json_data


@pytest.fixture
def client():
    return Client(APIKEY, security={'policy': b64encode(b'somepolicy'), 'signature': 'somesignature'})


def test_api_set(client):
    assert client.apikey == APIKEY


def test_wrong_storage():
    kwargs = {'apikey': APIKEY, 'storage': 'googlecloud'}
    pytest.raises(DataError, Client, **kwargs)


def test_store(client):
    @urlmatch(netloc=r'cdn.filestackcontent\.com', method='post', scheme='https')
    def api_store(url, request):
        return response(200, {'url': 'https://cdn.filestackcontent.com/{}'.format(HANDLE)})

    with HTTMock(api_store):
        filelink = client.upload(url="someurl", params={'filename': 'something.jpg'}, multipart=False)

    assert isinstance(filelink, Filelink)
    assert filelink.handle == HANDLE


def test_store_filepath(client):
    @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/store', method='post', scheme='https')
    def api_store(url, request):
        return response(200, {'url': 'https://cdn.filestackcontent.com/{}'.format(HANDLE)})

    with HTTMock(api_store):
        filelink = client.upload(filepath="tests/data/bird.jpg", multipart=False)

    assert isinstance(filelink, Filelink)
    assert filelink.handle == HANDLE


def test_wrong_store_params(client):
    kwargs = {'params': {'call': 'someparameter'}, 'url': 'someurl'}
    pytest.raises(DataError, client.upload, **kwargs)


def test_bad_store_params(client):
    kwargs = {'params': {'access': True}, 'url': 'someurl'}
    pytest.raises(DataError, client.upload, **kwargs)


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


@pytest.mark.parametrize('store_params, expected_url_part', [
    [{'filename': 'image.jpg'}, 'filename:image.jpg'],
    [{'location': 'S3'}, 'location:S3'],
    [{'path': 'some_path'}, 'path:some_path'],
    [{'container': 'container_id'}, 'container:container_id'],
    [{'region': 'us-east-1'}, 'region:us-east-1'],
    [{'access': 'public'}, 'access:public'],
    [{'base64decode': True}, 'base64decode:True'],
    [{'workflows': ['workflows_id_1']}, 'workflows:[%22workflows_id_1%22]']
])
def test_url_store_task(store_params, expected_url_part, client):
    @urlmatch(netloc=r'cdn.filestackcontent\.com', method='post', scheme='https')
    def api_store(url, request):
        assert expected_url_part in request.url
        return response(200, {'url': 'https://cdn.filestackcontent.com/{}'.format(HANDLE)})

    with HTTMock(api_store):
        filelink = client.upload(url="someurl", params=store_params, multipart=False)

    assert isinstance(filelink, Filelink)
    assert filelink.handle == HANDLE


@patch('requests.put')
@patch('requests.post')
def test_upload_multipart_workflows(post_mock, put_mock, client):

    workflow_ids = ['workflow-id-1', 'workflow-id-2']
    store_params = {'workflows': workflow_ids}
    put_mock.return_value = MockResponse()

    post_mock.side_effect = [
        MockResponse(),
        MockResponse(),
        MockResponse(json={'handle': 'new_handle'})
    ]

    new_filelink = client.upload(
        filepath='tests/data/bird.jpg',
        params=store_params,
        multipart=True
    )

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
