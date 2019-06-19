from unittest.mock import mock_open, patch

import pytest
from trafaret import DataError
from httmock import urlmatch, HTTMock, response

from filestack import Filelink, Security
from filestack.config import CDN_URL

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'
SECURITY = Security({'call': ['read'], 'expiry': 10238239}, 'APPSECRET')


@pytest.fixture
def filelink():
    return Filelink(HANDLE, apikey=APIKEY)


@pytest.fixture
def secure_filelink():
    return Filelink(HANDLE, apikey=APIKEY, security=SECURITY)


def test_handle(filelink):
    assert filelink.handle == HANDLE


def test_url(filelink):
    url = CDN_URL + '/' + HANDLE
    assert url == filelink.url


def test_get_content(filelink):
    @urlmatch(netloc=r'cdn.filestackcontent\.com', method='get', scheme='https')
    def api_download(url, request):
        return response(200, b'SOMEBYTESCONTENT')

    with HTTMock(api_download):
        content = filelink.get_content()

    assert content == b'SOMEBYTESCONTENT'


def test_bad_call(filelink):
    @urlmatch(netloc=r'cdn.filestackcontent\.com', method='get', scheme='https')
    def api_bad(url, request):
        return response(400, b'SOMEBYTESCONTENT')

    with HTTMock(api_bad):
        pytest.raises(Exception, filelink.get_content)


def test_get_metadata(filelink):
    @urlmatch(netloc=r'cdn.filestackcontent.com', path=r'/\w+/metadata', method='get', scheme='https')
    def api_metadata(url, request):
        return response(200, '{"filename": "somefile.jpg"}')

    with HTTMock(api_metadata):
        metadata_response = filelink.get_metadata()
        metadata = metadata_response

    assert metadata['filename'] == 'somefile.jpg'


def test_download(filelink):
    @urlmatch(netloc=r'cdn\.filestackcontent\.com', method='get', scheme='https')
    def api_download(url, request):
        return response(200, b'file-content')

    m = mock_open()
    with patch('filestack.mixins.filestack_common.open', m):
        with HTTMock(api_download):
            file_size = filelink.download('tests/data/test_download.jpg')
            assert file_size == 12
    m().write.assert_called_once_with(b'file-content')


def test_overwrite_content(secure_filelink):
    @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/file', method='post', scheme='https')
    def api_delete(url, request):
        return response(200, {'handle': HANDLE})

    with HTTMock(api_delete):
        filelink_response = secure_filelink.overwrite(url="http://www.someurl.com")

    assert filelink_response.status_code == 200


def test_overwrite_content_filepath(secure_filelink):
    @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/file', method='post', scheme='https')
    def api_delete(url, request):
        return response(200, {'handle': HANDLE})

    with HTTMock(api_delete):
        filelink_response = secure_filelink.overwrite(filepath='tests/data/bird.jpg')

    assert filelink_response.status_code == 200


def test_overwrite_argument_fail(filelink):
    # passing in neither the url or filepath parameter
    pytest.raises(ValueError, filelink.overwrite)


def test_overwrite_bad_params(secure_filelink):
    kwargs = {'params': {'call': ['read']}}
    pytest.raises(DataError, secure_filelink.overwrite, **kwargs)


def test_overwrite_bad_param_value(secure_filelink):
    kwargs = {'params': {'base64decode': 'true'}}
    pytest.raises(DataError, secure_filelink.overwrite, **kwargs)
