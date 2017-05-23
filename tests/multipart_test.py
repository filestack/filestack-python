import hashlib
import json
import mimetypes
import mock
import os.path
import pytest
import requests
import responses

from filestack import Client, Filelink
from filestack.config import MULTIPART_START_URL, MULTIPART_UPLOAD_URL, MULTIPART_COMPLETE_URL
from filestack.utils import upload_utils

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'
URL = "https://cdn.filestackcontent.com/{}".format(HANDLE)


class FakeHash(object):
    def digest(bytes):
        return b'this is some byte code'


def chunk_put_callback(request):
    body = {'url': URL}
    return (200, {'ETag': 'someetags'}, json.dumps(body))


@pytest.fixture
def client():
    return Client(APIKEY)


def mock_filename(path):
    return [None, 'notbird.jpg']


def mock_filesize(path):
    return 10 * 1024 ** 2


def mock_mimetype(path):
    return [None, 'image/jpeg']


def mock_md5(chunk):
    return FakeHash()


@responses.activate
def test_upload_multipart(monkeypatch, client):

    # mock all the functions we need that operate on the file/operating system
    monkeypatch.setattr(hashlib, 'md5', mock_md5)
    monkeypatch.setattr(os.path, 'split', mock_filename)
    monkeypatch.setattr(os.path, 'getsize', mock_filesize)
    monkeypatch.setattr(mimetypes, 'guess_type', mock_mimetype)

    # add the different HTTP responses that are called during the multipart upload
    responses.add(responses.POST, MULTIPART_START_URL, status=200, content_type="application/json",
                  json={"region": "us-east-1", "upload_id": "someuuid", "uri": "someuri", "location_url": "somelocation"})
    responses.add(responses.POST, MULTIPART_UPLOAD_URL, status=200, content_type="application/json", json={'url': URL, "headers": {}})
    responses.add_callback(responses.PUT, URL, callback=chunk_put_callback)
    responses.add(responses.POST, MULTIPART_COMPLETE_URL, status=200, content_type="application/json", json={"url": URL})

    # we also need to mock opening a file
    open_mock = mock.MagicMock()
    with mock.patch('__builtin__.open', open_mock):

        new_filelink = client.upload(filepath='bird.jpg')

        assert new_filelink.handle == HANDLE

