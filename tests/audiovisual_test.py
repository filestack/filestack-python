import pytest
import responses

from filestack import AudioVisual, Filelink


APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'
URL = 'https://cdn.filestackcontent.com/{}'.format(HANDLE)
PROCESS_URL = 'https://process.filestackapi.com/{}'.format(HANDLE)


@pytest.fixture
def av():
    return AudioVisual(PROCESS_URL, 'someuuid', 'sometimetstamp', apikey=APIKEY)


@responses.activate
def test_status(av):
    responses.add(responses.GET, 'https://process.filestackapi.com/SOMEHANDLE', json={'status': 'completed'})
    assert av.status == 'completed'


@responses.activate
def test_convert(av):
    responses.add(
        responses.GET, 'https://process.filestackapi.com/SOMEHANDLE',
        json={'status': 'completed', 'data': {'url': URL}}
    )
    filelink = av.to_filelink()
    assert isinstance(filelink, Filelink)
    assert filelink.handle == HANDLE
