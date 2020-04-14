import io
import json
from collections import defaultdict
from unittest.mock import patch

import responses
from httmock import HTTMock, response, urlmatch

from tests.helpers import DummyHttpResponse
from filestack import Client
from filestack import config
from filestack.uploads.multipart import upload_chunk, Chunk

APIKEY = 'APIKEY'
HANDLE = 'SOMEHANDLE'
URL = 'https://cdn.filestackcontent.com/{}'.format(HANDLE)


def chunk_put_callback(request):
    body = {'url': URL}
    return 200, {'ETag': 'someetags'}, json.dumps(body)


@responses.activate
def test_upload_filepath():
    client = Client(APIKEY)

    # add the different HTTP responses that are called during the multipart upload
    responses.add(
        responses.POST, config.MULTIPART_START_URL, status=200, content_type='application/json',
        json={'region': 'us-east-1', 'upload_id': 'someuuid', 'uri': 'someuri', 'location_url': 'fs-uploads.com'}
    )
    responses.add(
        responses.POST, 'https://fs-uploads.com/multipart/upload',
        status=200, content_type='application/json', json={'url': URL, 'headers': {}}
    )
    responses.add_callback(responses.PUT, URL, callback=chunk_put_callback)
    responses.add(
        responses.POST, 'https://fs-uploads.com/multipart/complete', status=200,
        content_type='application/json', json={'url': URL, 'handle': HANDLE}
    )

    new_filelink = client.upload(filepath='tests/data/doom.mp4')
    assert new_filelink.handle == HANDLE


@patch('filestack.uploads.multipart.requests.put')
@patch('filestack.uploads.multipart.requests.post')
def test_upload_file_obj(post_mock, put_mock):
    start_response = defaultdict(str)
    start_response['location_url'] = 'fs.api'
    post_mock.side_effect = [
        DummyHttpResponse(json_dict=start_response),
        DummyHttpResponse(json_dict=defaultdict(str)),
        DummyHttpResponse(json_dict={'handle': 'bytesHandle'})
    ]
    put_mock.return_value = DummyHttpResponse(
        json_dict=defaultdict(str), headers={'ETag': 'etag-1'}
    )
    file_content = b'file bytes'
    filelink = Client(APIKEY).upload(file_obj=io.BytesIO(file_content))
    assert filelink.handle == 'bytesHandle'
    put_args, put_kwargs = put_mock.call_args
    assert put_kwargs['data'] == file_content


def test_upload_chunk():
    @urlmatch(netloc=r'fsuploads\.com', path='/multipart/upload', method='post', scheme='https')
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

    chunk = Chunk(num=123, seek_point=0, filepath='tests/data/doom.mp4')
    start_response = defaultdict(str)
    start_response['location_url'] = 'fsuploads.com'
    with HTTMock(fs_backend_mock), HTTMock(amazon_mock):
        upload_result = upload_chunk('apikey', 'filename', 's3', start_response, chunk)
        assert upload_result == {'part_number': 123, 'etag': 'etagX'}
