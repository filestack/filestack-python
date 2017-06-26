import filestack.models
import pytest

from base64 import b64encode
from filestack import Client, Filelink, Transform
from filestack.exceptions import FilestackException
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
    @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/store', method='post', scheme='https')
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
