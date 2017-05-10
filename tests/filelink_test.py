import pytest

from filestack import Client, Filelink, security
from httmock import urlmatch, HTTMock, response, all_requests
from trafaret import DataError

APIKEY  = 'APIKEY'
HANDLE = 'SOMEHANDLE'

FILESTACK_CDN_URL = 'https://cdn.filestackcontent.com/'
filelink = Filelink(HANDLE, apikey=APIKEY)

SECURITY = security({'call': ['read'], 'expiry': 10238239}, 'APPSECRET')
secure_filelink = Filelink(HANDLE, apikey=APIKEY, security=SECURITY)

def test_handle():
    assert filelink.handle == HANDLE

def test_apikey_default():
    filelink_default = Filelink(HANDLE)
    assert filelink_default.apikey == None

def test_api_get():
    assert APIKEY == filelink.apikey

def test_api_set():
    NEW_APIKEY = 'ANOTHER_APIKEY'
    filelink.apikey = NEW_APIKEY
    assert NEW_APIKEY == filelink.apikey

def test_url():
    url = FILESTACK_CDN_URL + HANDLE
    assert url == filelink.url

def test_get_content():
    @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/file', method='get', scheme='https')
    def api_download(url, request):
        return response(200, b'SOMEBYTESCONTENT')

    with HTTMock(api_download):
        content = filelink.get_content()

    assert content == b'SOMEBYTESCONTENT'

def test_get_content_params():
    @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/file', method='get', scheme='https')
    def api_download(url, request):
        return response(200, b'SOMEBYTESCONTENT')

    with HTTMock(api_download):
        content = filelink.get_content(params={'dl': True})

    assert content == b'SOMEBYTESCONTENT'

def test_get_content_bad_params():
    kwargs = {'params': {'call': ['read']}}
    pytest.raises(DataError, filelink.get_content, **kwargs)

def test_get_content_bad_param_value():
    kwargs = {'params': {'dl': 'true'}}
    pytest.raises(DataError, filelink.get_content, **kwargs)

def test_get_content():
    @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/file', method='get', scheme='https')
    def api_download(url, request):
        return response(200, b'SOMEBYTESCONTENT')

    with HTTMock(api_download):
        content = filelink.get_content()

    assert content == b'SOMEBYTESCONTENT'

def test_download_bad_params():
    kwargs = {'params': {'call': ['read']}}
    pytest.raises(DataError, filelink.download, 'somepath', **kwargs)

def test_download_bad_param_value():
    kwargs = {'params': {'dl': 'true'}}
    pytest.raises(DataError, filelink.download, 'somepath', **kwargs)

def test_overwrite_content():
    @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/file', method='post', scheme='https')
    def api_delete(url, request):
        return response(200, {'handle': HANDLE})

    with HTTMock(api_delete):
        filelink_response = secure_filelink.overwrite(url="http://www.someurl.com")

    assert filelink_response.status_code == 200

def test_overwrite_argument_fail():
    # passing in neither the url or filepath parameter
    pytest.raises(ValueError, filelink.overwrite)

def test_overwrite_bad_params():
    kwargs = {'params': {'call': ['read']}}
    pytest.raises(DataError, secure_filelink.overwrite, **kwargs)

def test_overwrite_bad_param_value():
    kwargs = {'params': {'base64decode': 'true'}}
    pytest.raises(DataError, secure_filelink.overwrite, **kwargs)
