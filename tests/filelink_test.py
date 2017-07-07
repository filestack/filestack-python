import pytest

from base64 import b64encode
from filestack import Filelink, security
from filestack.config import CDN_URL
from httmock import urlmatch, HTTMock, response
from trafaret import DataError

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'


@pytest.fixture
def filelink():
    return Filelink(HANDLE, apikey=APIKEY)

SECURITY = security({'call': ['read'], 'expiry': 10238239}, 'APPSECRET')

@pytest.fixture
def secure_filelink():
    return Filelink(HANDLE, apikey=APIKEY, security=SECURITY)


def test_handle(filelink):
    assert filelink.handle == HANDLE


def test_apikey_default():
    filelink_default = Filelink(HANDLE)
    assert filelink_default.apikey == None


def test_api_get(filelink):
    assert APIKEY == filelink.apikey


def test_api_set(filelink):
    NEW_APIKEY = 'ANOTHER_APIKEY'
    filelink.apikey = NEW_APIKEY
    assert NEW_APIKEY == filelink.apikey


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
    @urlmatch(netloc=r'cdn.filestackcontent.com', method='get', scheme='https')
    def api_metadata(url, request):
        return response(200, '{"filename": "somefile.jpg"}')

    with HTTMock(api_metadata):
        metadata_response = filelink.get_metadata()
        metadata = metadata_response

    assert metadata['filename'] == 'somefile.jpg'


def test_get_content_params(filelink):
    @urlmatch(netloc=r'cdn.filestackcontent\.com', method='get', scheme='https')
    def api_download(url, request):
        return response(200, b'SOMEBYTESCONTENT')

    with HTTMock(api_download):
        content = filelink.get_content(params={'dl': True})

    assert content == b'SOMEBYTESCONTENT'


def test_delete(filelink):
    @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/file', method='delete', scheme='https')
    def test_delete(url, request):
        return response(200)

    with HTTMock(test_delete):
        delete_response = filelink.delete()

    assert delete_response.status_code


def test_get_content_bad_params(filelink):
    kwargs = {'params': {'call': ['read']}}
    pytest.raises(DataError, filelink.get_content, **kwargs)


def test_get_content_bad_param_value(filelink):
    kwargs = {'params': {'dl': 'true'}}
    pytest.raises(DataError, filelink.get_content, **kwargs)


def test_download_bad_params(filelink):
    kwargs = {'params': {'call': ['read']}}
    pytest.raises(DataError, filelink.download, 'somepath', **kwargs)


def test_download_bad_param_value(filelink):
    kwargs = {'params': {'dl': 'true'}}
    pytest.raises(DataError, filelink.download, 'somepath', **kwargs)


def test_download(filelink):
    @urlmatch(netloc=r'cdn.filestackcontent\.com', method='get', scheme='https')
    def api_download(url, request):
        with open('tests/data/bird.jpg', 'rb') as f:
            return response(200, b64encode(f.read()))

    with HTTMock(api_download):
        download_response = filelink.download('tests/data/test_download.jpg')
        assert download_response.status_code == 200

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

def test_tags(secure_filelink):
    @urlmatch(netloc=r'cdn.filestackcontent.com', method='get', scheme='https')
    def tag_request(url, request):
        return response(200, {'tags': {'auto': {'tag': 100}}})

    with HTTMock(tag_request):
        tag_response = secure_filelink.tags()
        assert tag_response['tags']['auto']['tag'] == 100

def test_unsecure_tags(filelink):
    pytest.raises(Exception, filelink.tags)
