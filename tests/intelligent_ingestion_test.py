import json

import pytest
import responses

from filestack.uploads.intelligent_ingestion import upload_part


@responses.activate
def test_upload_part_success():
    responses.add(
        responses.POST, 'https://fs-upload.com/multipart/upload',
        json={'url': 'http://s3.url', 'headers': {'filestack': 'headers'}}
    )
    responses.add(responses.PUT, 'http://s3.url')
    responses.add(responses.POST, 'https://fs-upload.com/multipart/commit')

    part = {'seek_point': 0, 'num': 1}
    start_response = {
        'uri': 'fs-upload.com', 'location_url': 'fs-upload.com', 'region': 'region', 'upload_id': 'abc'
    }
    upload_part('Aaaaapikey', 'file.txt', 'tests/data/doom.mp4', 1234, 's3', start_response, part)
    multipart_upload_payload = json.loads(responses.calls[0].request.body.decode())
    assert multipart_upload_payload == {
        'apikey': 'Aaaaapikey', 'uri': 'fs-upload.com', 'region': 'region',
        'upload_id': 'abc', 'store': {'location': 's3'},
        'part': 1, 'size': 5415034, 'md5': 'IuNjhgPo2wbzGFo6f7WhUA==', 'offset': 0, 'fii': True
    }
    with open('tests/data/doom.mp4', 'rb') as f:
        assert responses.calls[1].request.body == f.read()
    multipart_commit_payload = json.loads(responses.calls[2].request.body.decode())
    assert multipart_commit_payload == {
        'apikey': 'Aaaaapikey', 'uri': 'fs-upload.com', 'region': 'region',
        'upload_id': 'abc', 'store': {'location': 's3'}, 'part': 1, 'size': 1234
    }


@responses.activate
def test_upload_part_with_resize():
    responses.add(
        responses.POST, 'https://fs-upload.com/multipart/upload',
        json={'url': 'https://s3.url', 'headers': {'filestack': 'headers'}}
    )
    responses.add(responses.PUT, 'https://s3.url', status=400)
    responses.add(responses.PUT, 'https://s3.url')  # chunks 1 & 2 of part 1
    responses.add(responses.POST, 'https://fs-upload.com/multipart/commit')

    start_response = {
        'uri': 'fs-upload.com', 'location_url': 'fs-upload.com', 'region': 'region', 'upload_id': 'abc'
    }
    part = {'seek_point': 0, 'num': 1}
    upload_part('Aaaaapikey', 'file.txt', 'tests/data/doom.mp4', 5415034, 's3', start_response, part)

    responses.assert_call_count('https://fs-upload.com/multipart/upload', 3)
    responses.assert_call_count('https://s3.url', 3)
    assert len(responses.calls[1].request.body) == 5415034
    assert len(responses.calls[3].request.body) == 4194304
    assert len(responses.calls[5].request.body) == 1220730


@responses.activate
def test_min_chunk_size_exception():
    responses.reset()
    responses.add(
        responses.POST, 'https://fs-upload.com/multipart/upload',
        json={'url': 'https://upload.url', 'headers': {'filestack': 'headers'}}
    )
    responses.add(responses.PUT, 'https://upload.url', status=400)

    part = {'seek_point': 0, 'num': 1}
    start_response = {
        'uri': 'fs-upload.com', 'location_url': 'fs-upload.com', 'region': 'region', 'upload_id': 'abc'
    }
    with pytest.raises(Exception, match='Minimal chunk size failed'):
        upload_part('Aaaaapikey', 'file.txt', 'tests/data/doom.mp4', 5415034, 's3', start_response, part)

    chunk_sizes = [len(call.request.body) for call in responses.calls if call.request.method == 'PUT']
    assert chunk_sizes[-1] == 32768  # check size of last attempt
