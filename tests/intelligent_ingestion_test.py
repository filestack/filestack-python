import json
import time
from multiprocessing import Process, Queue
from collections import defaultdict

import pytest
from httmock import urlmatch, HTTMock, all_requests

from filestack.utils.intelligent_ingestion import (
    UploadManager,
    commit_part,
    consume_upload_job
)


@pytest.fixture
def upload_manager():
    return UploadManager(
        apikey='Axxxxxxxxxxxz',
        filepath='tests/data/doom.mp4',
        storage='s3',
        params=None, security=None,
        upload_q=Queue(), commit_q=Queue(), response_q=Queue()
    )


def test_multipart_start(upload_manager):
    @urlmatch(netloc=r'upload\.filestackapi\.com', path='/multipart/start', method='post', scheme='https')
    def multipart_start_mock(url, request):
        return {
            'status_code': 200,
            'content': json.dumps({
                'upload_id': 'my-upload-id',
                'region': 'eu-west-1',
                'uri': '/upload/apikey/image.jpg',
            })
        }

    assert upload_manager.start_response is None

    with HTTMock(multipart_start_mock):
        upload_manager._multipart_start()

    assert upload_manager.start_response == {
        'upload_id': 'my-upload-id',
        'region': 'eu-west-1',
        'uri': '/upload/apikey/image.jpg',
    }


def test_create_parts(upload_manager):
    chunk_size = 1024 ** 2  # 1 MB
    upload_manager.chunk_size = chunk_size
    upload_manager._create_parts()
    assert len(upload_manager.parts) == 1
    assert len(upload_manager.parts[1]['chunks']) == 6

    offset = 0
    chunks = list(upload_manager.parts[1]['chunks'])[::-1]
    first_five, last = chunks[:5], chunks[-1]
    for chunk in first_five:
        assert chunk['size'] == chunk_size
        assert chunk['offset'] == offset
        offset += chunk_size

    assert last['size'] == 172154
    assert last['offset'] == 5242880


def test_split_chunk(upload_manager):
    chunk = {'size': 5 * 1024 ** 2, 'offset': 0}
    upload_manager.chunk_size = 2 * 1024 ** 2
    assert upload_manager._split_chunk(chunk) == [
        {'size': 2097152, 'offset': 0},
        {'size': 2097152, 'offset': 2097152},
        {'size': 1048576, 'offset': 4194304}
    ]


def test_get_next_chunk(upload_manager):
    upload_manager._create_parts()

    # with detaulf part/chunk size, there should only be one part and one chunk
    part_num, chunk = upload_manager._get_next_chunk()
    assert part_num == 1
    assert chunk == {'size': 5415034, 'offset': 0}

    part_num, chunk = upload_manager._get_next_chunk()
    assert part_num is None
    assert chunk is None


def test_commit_part():
    @urlmatch(netloc=r'upload\.filestackapi\.com', path='/multipart/commit', method='post', scheme='https')
    def multipart_commit_mock(url, request):
        return {'status_code': 200, 'content': b''}

    commit_q, response_q = Queue(), Queue()

    with HTTMock(multipart_commit_mock):
        commit_q.put({
            'apikey': 'Axxxz',
            'uri': '/some/uri',
            'region': 'us-east-1',
            'upload_id': 'some-id',
            'size': 1,
            'part': 11,
            'store_location': 's3',
            'filename': 'image.jpg'
        })
        commit_q.put('die')
        commit_part(commit_q, response_q)

    response = response_q.get()
    assert response == {'part': 11, 'worker': 'committer', 'success': True}


def test_upload_chunk():
    @urlmatch(netloc=r'upload\.filestackapi\.com', path='/multipart/upload', method='post', scheme='https')
    def backend_mock(url, request):
        return {
            'status_code': 200,
            'content': json.dumps({
                'headers': None,
                'url': 'https://amazon.com/upload',
            })
        }

    @urlmatch(netloc=r'amazon\.com', path='/upload', method='put', scheme='https')
    def s3_mock(url, request):
        return {'status_code': 200}

    upload_q, response_q = Queue(), Queue()
    job = defaultdict(str)
    job['filepath'] = 'tests/data/doom.mp4'
    job['part'] = 77
    job['seek'] = 0
    job['offset'] = 0
    job['size'] = 1

    upload_q.put(job)
    upload_q.put('die')
    with HTTMock(backend_mock), HTTMock(s3_mock):
        consume_upload_job(upload_q, response_q)

    response = response_q.get()
    assert response['success'] is True
    assert response['part'] == 77
