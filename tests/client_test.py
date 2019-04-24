import filestack.models
import pytest

from mock import patch
from base64 import b64encode
from filestack import Client, Filelink, Transform
from httmock import urlmatch, HTTMock, response
from trafaret import DataError


APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'


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
    [
        {
            'filename': 'image.jpg'
        },
        'filename:image.jpg'
    ],

    [
        {
            'location': 'S3'
        },
        'location:S3'
    ],

    [
        {
            'path': 'some_path'
        },
        'path:some_path'
    ],

    [
        {
            'container': 'container_id'
        },
        'container:container_id'
    ],

    [
        {
            'region': 'us-east-1'
        },
        'region:us-east-1'
    ],

    [
        {
            'access': 'public'
        },
        'access:public'
    ],

    [
        {
            'base64decode': True
        },
        'base64decode:True'
    ],

    [
        {
            'workflows': ['workflows_id_1']
        },
        'workflows:[%22workflows_id_1%22]'
    ]
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


@pytest.mark.parametrize('request_data, expected_request_data', [
    [
        {
            'workflows': ['workflows_id']
        },
        {
            'workflows': '["workflows_id"]'
        }
    ]
])
@patch('requests.put')
@patch('requests.post')
def test_upload_multipart_workflows(post_mock, put_mock, request_data, expected_request_data, client):

    new_filelink = client.upload(
        filepath='tests/data/bird.jpg',
        params=request_data,
        multipart=True
    )

    assert all(key in post_mock.call_args[1]['data'] and post_mock.call_args[1]['data'][key] == value
               for key, value in expected_request_data.items())
    assert isinstance(new_filelink, Filelink)
