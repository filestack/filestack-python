import pytest

from filestack import AudioVisual, Filelink
from httmock import urlmatch, HTTMock, response


APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'
URL = 'https://cdn.filestackcontent.com/{}'.format(HANDLE)
PROCESS_URL = 'https://process.filestackapi.com/{}'.format(HANDLE)


@pytest.fixture
def av():
    return AudioVisual(PROCESS_URL, 'someuuid', 'sometimetstamp', apikey=APIKEY)


def test_status(av):

    @urlmatch(netloc=r'process.filestackapi\.com', method='get', scheme='https')
    def api_zip(url, request):
        return response(200, {'url': PROCESS_URL, 'status': 'completed'}, {'content-type': 'application/json'})

    with HTTMock(api_zip):
        assert av.status == 'completed'


def test_convert(av):

    @urlmatch(netloc=r'process.filestackapi\.com', method='get', scheme='https')
    def api_zip(url, request):
        return response(200, {'status': 'completed', 'data': {'url': URL}}, {'content-type': 'application/json'})

    with HTTMock(api_zip):
        filelink = av.to_filelink()
        assert isinstance(filelink, Filelink)
        assert filelink.handle == HANDLE
