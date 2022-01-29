import io
import re
from unittest.mock import mock_open, patch, ANY

import pytest
import responses

from filestack import exceptions
from filestack import Filelink, Security
from filestack import config

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'
SECURITY = Security({'call': ['read'], 'expiry': 10238239}, 'APPSECRET')


@pytest.fixture
def filelink():
    yield Filelink(HANDLE, apikey=APIKEY)


@pytest.fixture
def secure_filelink():
    yield Filelink(HANDLE, apikey=APIKEY, security=SECURITY)


def test_handle(filelink):
    assert filelink.handle == HANDLE


def test_url(filelink):
    url = config.CDN_URL + '/' + HANDLE
    assert url == filelink.url


@pytest.mark.parametrize('security_obj, expected_security_part', [
    [
        None,
        (
            'security=p:eyJjYWxsIjogWyJyZWFkIl0sICJleHBpcnkiOiAxMDIzODIzOX0=,'
            's:858d1ee9c0a1f06283e495f78dc7950ff6e64136ce960465f35539791fcd486b'
        )
    ],
    [
        Security({'call': ['write'], 'expiry': 1655992432}, 'another-secret'),
        (
            'security=p:eyJjYWxsIjogWyJ3cml0ZSJdLCAiZXhwaXJ5IjogMTY1NTk5MjQzMn0=,'
            's:625cc5b9beab3e939fb53935f7795919c9f57f628d43adfc14566d2ad9a4ad47'
        )
    ],
])
def test_signed_url(security_obj, expected_security_part, secure_filelink):
    assert expected_security_part in secure_filelink.signed_url(security=security_obj)


@responses.activate
def test_get_content(filelink):
    responses.add(
        responses.GET, 'https://cdn.filestackcontent.com/{}'.format(HANDLE), body=b'file-content'
    )
    content = filelink.get_content()
    assert content == b'file-content'


@responses.activate
def test_bad_call(filelink):
    responses.add(
        responses.GET, 'https://cdn.filestackcontent.com/{}'.format(HANDLE), status=400
    )
    with pytest.raises(exceptions.FilestackHTTPError):
        filelink.get_content()


@pytest.mark.parametrize('attributes, security, expected_params', [
    (None, None, {}),
    (
        None,
        Security({'expiry': 123}, 'secret'),
        {
            'policy': 'eyJleHBpcnkiOiAxMjN9',
            'signature': '4de8b7441b3daf0d68b4f8ebcf7e015d07aef43a1295476a1dde1aed327abc01'
        }
    ),
    (
        ['size', 'filename'],
        Security({'expiry': 123}, 'secret'),
        {
            'size': 'true',
            'filename': 'true',
            'policy': 'eyJleHBpcnkiOiAxMjN9',
            'signature': '4de8b7441b3daf0d68b4f8ebcf7e015d07aef43a1295476a1dde1aed327abc01'
        }
    ),
])
@responses.activate
def test_metadata(attributes, security, expected_params, filelink):
    responses.add(
        responses.GET,
        re.compile('https://cdn.filestackcontent.com/SOMEHANDLE/metadata.*'),
        json={'metadata': 'content'}
    )
    metadata_response = filelink.metadata(attributes_list=attributes, security=security)
    assert metadata_response == {'metadata': 'content'}
    assert responses.calls[0].request.params == expected_params


@responses.activate
def test_download(filelink):
    responses.add(
        responses.GET, 'https://cdn.filestackcontent.com/{}'.format(HANDLE), body=b'file-content'
    )
    m = mock_open()
    with patch('filestack.mixins.common.open', m):
        file_size = filelink.download('tests/data/test_download.jpg')
        assert file_size == 12
    m().write.assert_called_once_with(b'file-content')


def test_tags_without_security(filelink):
    with pytest.raises(Exception, match=r'Security is required'):
        filelink.tags()


@responses.activate
def test_tags(secure_filelink):
    responses.add(
        responses.GET, re.compile('https://cdn.filestackcontent.com/tags/.*/{}$'.format(HANDLE)),
        json={'tags': {'cat': 98}}
    )
    assert secure_filelink.tags() == {'tags': {'cat': 98}}
    assert responses.calls[0].request.url == '{}/tags/{}/{}'.format(config.CDN_URL, SECURITY.as_url_string(), HANDLE)


@responses.activate
def test_tags_on_transformation(secure_filelink):
    transformation = secure_filelink.resize(width=100)
    image_tags = {'tags': {'cat': 99}}
    responses.add(
        responses.GET, re.compile('{}/resize.*/{}$'.format(config.CDN_URL, HANDLE)),
        json=image_tags
    )
    assert transformation.tags() == image_tags
    assert responses.calls[0].request.url == '{}/resize=width:100/tags/{}/{}'.format(
        config.CDN_URL, SECURITY.as_url_string(), HANDLE
    )


def test_sfw_without_security(filelink):
    with pytest.raises(Exception, match=r'Security is required'):
        filelink.sfw()


@responses.activate
def test_sfw(secure_filelink):
    sfw_response = {'sfw': False}
    responses.add(responses.GET, re.compile('{}.*'.format(config.CDN_URL)), json=sfw_response)
    assert secure_filelink.sfw() == sfw_response
    assert responses.calls[0].request.url == '{}/sfw/{}/{}'.format(config.CDN_URL, SECURITY.as_url_string(), HANDLE)


@responses.activate
def test_sfw_on_transformation(secure_filelink):
    transformation = secure_filelink.resize(width=100)
    sfw_response = {'sfw': True}
    responses.add(responses.GET, re.compile('{}/resize.*'.format(config.CDN_URL)), json=sfw_response)
    assert transformation.sfw() == sfw_response
    assert responses.calls[0].request.url == '{}/resize=width:100/sfw/{}/{}'.format(
        config.CDN_URL, SECURITY.as_url_string(), HANDLE
    )


def test_overwrite_without_security(filelink):
    with pytest.raises(Exception, match='Security is required'):
        filelink.overwrite(url='https://image.url')


def test_invalid_overwrite_call(secure_filelink):
    with pytest.raises(Exception, match='filepath, file_obj or url argument must be provided'):
        secure_filelink.overwrite(base64decode=True)


@pytest.mark.parametrize('decode_base64', [True, False])
@patch('filestack.models.filelink.requests.post')
def test_overwrite_with_url(post_mock, decode_base64, secure_filelink):
    secure_filelink.overwrite(url='http://image.url', base64decode=decode_base64)
    post_mock.assert_called_once_with(
        'https://www.filestackapi.com/api/file/{}'.format(HANDLE),
        data={'url': 'http://image.url'},
        params={
            'policy': SECURITY.policy_b64,
            'signature': SECURITY.signature,
            'base64decode': 'true' if decode_base64 else 'false'
        }
    )


@patch('filestack.models.filelink.requests.post')
def test_overwrite_with_filepath(post_mock, secure_filelink):
    with patch('filestack.models.filelink.open', mock_open(read_data='content')) as m:
        secure_filelink.overwrite(filepath='path/to/file')
        post_mock.assert_called_once_with(
            'https://www.filestackapi.com/api/file/{}'.format(HANDLE),
            files={'fileUpload': ('filename', ANY, 'application/octet-stream')},
            params={
                'policy': SECURITY.policy_b64,
                'signature': SECURITY.signature,
                'base64decode': 'false'
            }
        )
        m.assert_called_once_with('path/to/file', 'rb')


@patch('filestack.models.filelink.requests.post')
def test_overwrite_with_file_obj(post_mock, secure_filelink):
    fobj = io.BytesIO(b'file-content')
    secure_filelink.overwrite(file_obj=fobj)
    post_mock.assert_called_once_with(
        'https://www.filestackapi.com/api/file/{}'.format(HANDLE),
        files={'fileUpload': ('filename', fobj, 'application/octet-stream')},
        params={
            'policy': SECURITY.policy_b64,
            'signature': SECURITY.signature,
            'base64decode': 'false'
        }
    )


@pytest.mark.parametrize('flink, exc_message', [
    (Filelink('handle', apikey=APIKEY), 'Security is required'),
    (Filelink('handle', security=SECURITY), 'Apikey is required')
])
def test_delete_without_apikey_or_security(flink, exc_message):
    with pytest.raises(Exception, match=exc_message):
        flink.delete()


@pytest.mark.parametrize('flink, security_arg', [
    (Filelink(HANDLE, apikey=APIKEY), SECURITY),
    (Filelink(HANDLE, apikey=APIKEY, security=SECURITY), None)
])
@patch('filestack.models.filelink.requests.delete')
def test_successful_delete(delete_mock, flink, security_arg):
    flink.delete(security=security_arg)
    delete_mock.assert_called_once_with(
        '{}/file/{}'.format(config.API_URL, HANDLE),
        params={
            'key': APIKEY,
            'policy': SECURITY.policy_b64,
            'signature': SECURITY.signature
        }
    )
