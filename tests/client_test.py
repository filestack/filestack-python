import pytest

from filestack import Client, Filelink
from httmock import urlmatch, HTTMock, response, all_requests
from trafaret import DataError

APIKEY  = 'APIKEY'
HANDLE = 'SOMEHANDLE'

client = Client(APIKEY)

def test_api_set():
    assert client.apikey == APIKEY

def test_wrong_storage():
    kwargs = {'apikey': APIKEY, 'storage': 'googlecloud'}
    pytest.raises(DataError, Client, **kwargs)

def test_store():
    @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/store', method='post', scheme='https')
    def api_store(url, request):
        return response(200, {'url': 'https://cdn.filestackcontent.com/{}'.format(HANDLE)})

    with HTTMock(api_store):
        filelink = client.upload(url="someurl")

    assert isinstance(filelink, Filelink)
    assert filelink.handle == HANDLE

def test_wrong_store_params():
    kwargs = {'params': {'call': 'someparameter'}, 'url': 'someurl'}
    pytest.raises(DataError, client.upload, **kwargs)

def test_bad_store_params():
    kwargs = {'params': {'access': True}, 'url': 'someurl'}
    pytest.raises(DataError, client.upload, **kwargs)

def test_invalid_client_method():
    pytest.raises(AttributeError, client.delete)
