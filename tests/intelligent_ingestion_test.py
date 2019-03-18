import json
from collections import defaultdict
try:
    from queue import Empty as QueueEmptyException
except ImportError:
    from Queue import Empty as QueueEmptyException

from multiprocessing import Process, Queue

import pytest
from httmock import urlmatch, HTTMock

from filestack.utils.intelligent_ingestion import (
    UploadManager,
    commit_part,
    consume_upload_job,
    manage_upload,
    upload
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


@urlmatch(netloc=r'upload\.filestackapi\.com', path='/multipart/complete', method='post', scheme='https')
def multipart_complete_mock(url, request):
    return {
        'status_code': 200,
        'content': json.dumps({'msg': 'ok'})
    }


@urlmatch(netloc=r'upload\.filestackapi\.com', path='/multipart/commit', method='post', scheme='https')
def multipart_commit_mock(url, request):
    return {'status_code': 200, 'content': b''}


@urlmatch(netloc=r'upload\.filestackapi\.com', path='/multipart/upload', method='post', scheme='https')
def fs_backend_mock(url, request):
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


def test_multipart_start(upload_manager):
    assert upload_manager.start_response is None

    with HTTMock(multipart_start_mock):
        upload_manager._multipart_start()

    assert upload_manager.start_response == {
        'upload_id': 'my-upload-id',
        'region': 'eu-west-1',
        'uri': '/upload/apikey/image.jpg',
    }


def test_multipart_complete(upload_manager):
    response_q = Queue()
    upload_manager.response_q = response_q
    upload_manager.start_response = defaultdict(str)

    with HTTMock(multipart_complete_mock):
        upload_manager._multipart_complete()

    assert response_q.get().json()['msg'] == 'ok'


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


def test_feed_uploaders(upload_manager):
    upload_q = Queue()
    chunk_size = 2 * 1024 ** 2
    upload_manager.upload_q = upload_q
    upload_manager.chunk_size = chunk_size
    upload_manager.start_response = defaultdict(str)
    upload_manager._create_parts()
    upload_manager._feed_uploaders()

    offset = 0
    for k in range(3):
        job = upload_q.get(block=True, timeout=1)
        assert job['chunk']['offset'] == offset
        offset += chunk_size

    assert upload_manager._currently_processed == 3
    # only 3 jobs should have been scheduled, so next get() should fail
    with pytest.raises(QueueEmptyException):
        upload_q.get(block=False)


def test_split_chunks_when_feeding(upload_manager):
    upload_q = Queue()
    upload_manager.upload_q = upload_q
    upload_manager.start_response = defaultdict(str)
    upload_manager._create_parts()
    assert len(upload_manager.parts[1]['chunks']) == 1

    chunk_size = 1 * 1024 ** 2
    upload_manager.chunk_size = chunk_size
    upload_manager._feed_uploaders()

    job = upload_q.get(block=True, timeout=1)
    assert job['chunk']['size'] == chunk_size


def test_commit_part():
    commit_q, response_q = Queue(), Queue()

    with HTTMock(multipart_commit_mock):
        job = defaultdict(str)
        job['size'] = 1
        job['part'] = 11
        commit_q.put(job)
        commit_q.put('die')
        commit_part(commit_q, response_q)

    response = response_q.get()
    assert response == {'part': 11, 'worker': 'committer', 'success': True}


def test_upload_chunk():
    upload_q, response_q = Queue(), Queue()
    job = defaultdict(str)
    job['filepath'] = 'tests/data/doom.mp4'
    job['part'] = 77
    job['seek'] = 0
    job['offset'] = 0
    job['size'] = 1

    upload_q.put(job)
    upload_q.put('die')
    with HTTMock(fs_backend_mock), HTTMock(s3_mock):
        consume_upload_job(upload_q, response_q)

    response = response_q.get()
    assert response['success'] is True
    assert response['part'] == 77
    assert response['delay'] == 0


def test_upload_chunk_with_fs_backend_500_error():
    @urlmatch(netloc=r'upload\.filestackapi\.com', path='/multipart/upload', method='post', scheme='https')
    def fs_backend_500_mock(url, request):
        return {
            'status_code': 500,
            'content': b''
        }

    upload_q, response_q = Queue(), Queue()
    job = defaultdict(str)
    job['filepath'] = 'tests/data/doom.mp4'
    job['part'] = 77
    job['seek'] = 0
    job['offset'] = 0
    job['size'] = 1

    upload_q.put(job)
    upload_q.put('die')
    with HTTMock(fs_backend_500_mock):
        consume_upload_job(upload_q, response_q)

    response = response_q.get()
    assert response['success'] is False
    assert response['part'] == 77
    assert response['delay'] == 1


def test_upload_chunk_with_fs_backend_network_error():
    @urlmatch(netloc=r'upload\.filestackapi\.com', path='/multipart/upload', method='post', scheme='https')
    def fs_backend_error(url, request):
        raise Exception('oops')

    upload_q, response_q = Queue(), Queue()
    job = defaultdict(str)
    job['filepath'] = 'tests/data/doom.mp4'
    job['part'] = 77
    job['seek'] = 0
    job['offset'] = 0
    job['size'] = 1

    upload_q.put(job)
    upload_q.put('die')
    with HTTMock(fs_backend_error):
        consume_upload_job(upload_q, response_q)

    response = response_q.get()
    assert response['success'] is False
    assert response['part'] == 77
    assert response['delay'] == 0


def test_upload_chunk_with_s3_network_error():
    @urlmatch(netloc=r'amazon\.com', path='/upload', method='put', scheme='https')
    def s3_with_error(url, request):
        raise Exception('oops')

    upload_q, response_q = Queue(), Queue()
    job = defaultdict(str)
    job['filepath'] = 'tests/data/doom.mp4'
    job['part'] = 77
    job['seek'] = 0
    job['offset'] = 0
    job['size'] = 1

    upload_q.put(job)
    upload_q.put('die')
    with HTTMock(fs_backend_mock, s3_with_error):
        consume_upload_job(upload_q, response_q)

    response = response_q.get()
    assert response['success'] is False
    assert response['part'] == 77
    assert response['delay'] == 0


def test_manage_upload_process():
    upload_q, commit_q, response_q = Queue(), Queue(), Queue()
    manager_proc = Process(
        target=manage_upload,
        name='manager',
        args=('Axxxz', 'tests/data/doom.mp4', 's3', None, None, upload_q, commit_q, response_q)
    )

    with HTTMock(multipart_start_mock), HTTMock(multipart_complete_mock):
        manager_proc.start()

    upload_job = upload_q.get(block=True, timeout=1)
    assert upload_job['chunk'] == {'offset': 0, 'size': 5415034}

    # tell the manager that the upload job failed (file size too big, no delay required)
    response_q.put({
        'worker': 'uploader',
        'chunk': upload_job['chunk'],
        'part': upload_job['part'],
        'offset': upload_job['offset'],
        'size': upload_job['size'],
        'success': False,
        'delay': 0
    })

    # failed job should be split into two new jobs
    job_1 = upload_q.get(block=True, timeout=1)
    job_2 = upload_q.get(block=True, timeout=1)

    # commit queue should be ampty
    with pytest.raises(QueueEmptyException):
        commit_q.get(block=False)

    # tell the manager that the 1st job was successful
    response_q.put({
        'worker': 'uploader',
        'chunk': job_1['chunk'],
        'part': job_1['part'],
        'offset': job_1['offset'],
        'size': job_1['size'],
        'success': True,
        'delay': 0
    })

    # and the 2nd failed and should be rescheduled
    response_q.put({
        'worker': 'uploader',
        'chunk': job_2['chunk'],
        'part': job_2['part'],
        'offset': job_2['offset'],
        'size': job_2['size'],
        'success': False,
        'delay': 1
    })

    # commit queue should still be ampty
    with pytest.raises(QueueEmptyException):
        commit_q.get(block=False)

    job_2_rescheduled = upload_q.get(block=True, timeout=1)
    assert job_2_rescheduled['delay'] == 1
    job_2.pop('delay')
    job_2_rescheduled.pop('delay')
    assert job_2 == job_2_rescheduled

    response_q.put({
        'worker': 'uploader',
        'chunk': job_2_rescheduled['chunk'],
        'part': job_2_rescheduled['part'],
        'offset': job_2_rescheduled['offset'],
        'size': job_2_rescheduled['size'],
        'success': True,
        'delay': 0
    })

    # manager should not schedule part 1 commit
    commit_job = commit_q.get(block=True, timeout=1)
    response_q.put({
        'worker': 'committer',
        'success': True,
        'part': commit_job['part']
    })

    # manager should now stop and /multipart/complete response should be
    # present in response_q
    assert response_q.get(block=True, timeout=1).json()['msg'] == 'ok'


def test_whole_upload():
    with HTTMock(multipart_start_mock), HTTMock(multipart_complete_mock), HTTMock(multipart_commit_mock), \
         HTTMock(fs_backend_mock), HTTMock(s3_mock):
        response = upload('Apikeyz', 'tests/data/doom.mp4', 's3')
    assert response.json()['msg'] == 'ok'
