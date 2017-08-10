import json
import pytest
from collections import defaultdict
import responses
from httmock import HTTMock, response, urlmatch

from filestack import Client
from filestack.config import MULTIPART_START_URL, MULTIPART_UPLOAD_URL, MULTIPART_COMPLETE_URL
from filestack.utils.upload_utils import upload_chunk

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'
URL = "https://cdn.filestackcontent.com/{}".format(HANDLE)


def chunk_put_callback(request):
    body = {'url': URL}
    return 200, {'ETag': 'someetags'}, json.dumps(body)


@pytest.fixture
def client():
    return Client(APIKEY)


@responses.activate
def test_upload_multipart(client):

    # add the different HTTP responses that are called during the multipart upload
    responses.add(responses.POST, MULTIPART_START_URL, status=200, content_type="application/json",
                  json={"region": "us-east-1", "upload_id": "someuuid", "uri": "someuri", "location_url": "somelocation"})
    responses.add(responses.POST, MULTIPART_UPLOAD_URL, status=200, content_type="application/json", json={'url': URL, "headers": {}})
    responses.add_callback(responses.PUT, URL, callback=chunk_put_callback)
    responses.add(responses.POST, MULTIPART_COMPLETE_URL, status=200, content_type="application/json", json={"url": URL})

    new_filelink = client.upload(filepath='tests/data/doom.mp4')
    assert new_filelink.handle == HANDLE


def test_upload_chunk():
    @urlmatch(netloc=r'upload\.filestackapi\.com', path='/multipart/upload', method='post', scheme='https')
    def fs_backend_mock(url, request):
        return {
            'status_code': 200,
            'content': json.dumps({
                'url': 'https://amazon.com/upload', 'headers': {'one': 'two'}
            })
        }

    @urlmatch(netloc=r'amazon\.com', path='/upload', method='put', scheme='https')
    def amazon_mock(url, request):
        return response(200, b'', {'ETag': 'etagX'}, reason=None, elapsed=0, request=request)

    job = defaultdict(str)
    job['seek'] = 0
    job['size'] = 0
    job['part'] = 123
    job['filepath'] = 'tests/data/doom.mp4'
    with HTTMock(fs_backend_mock), HTTMock(amazon_mock):
        assert upload_chunk('s3', job) == '123:etagX'
