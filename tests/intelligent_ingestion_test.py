from unittest.mock import patch, call, ANY
from collections import defaultdict

import pytest

from filestack import Security
from filestack.uploads.intelligent_ingestion import upload_part,  upload
from tests.helpers import DummyHttpResponse


@patch('filestack.uploads.intelligent_ingestion.requests.put')
@patch('filestack.uploads.intelligent_ingestion.requests.post')
def test_upload_part_success(post_mock, put_mock):
    post_mock.side_effect = [
        DummyHttpResponse(json_dict={'url': 'http://upload.url', 'headers': {'upload': 'headers'}}),
        DummyHttpResponse()
    ]

    put_mock.return_value = DummyHttpResponse()

    part = {'seek_point': 0, 'num': 1}
    upload_part(
        'Aaaaapikey', 'file.txt', 'tests/data/doom.mp4', 1234, 's3', defaultdict(lambda: 'fs-upload.com'), part
    )
    assert post_mock.call_args_list == [
        call(
            'https://fs-upload.com/multipart/upload',
            json={
                'apikey': 'Aaaaapikey', 'uri': 'fs-upload.com', 'region': 'fs-upload.com',
                'upload_id': 'fs-upload.com', 'store': {'location': 's3'},
                'part': 1, 'size': 5415034, 'md5': 'IuNjhgPo2wbzGFo6f7WhUA==', 'offset': 0, 'fii': True
            },
        ),
        call(
            'https://fs-upload.com/multipart/commit',
            json={
                'apikey': 'Aaaaapikey', 'uri': 'fs-upload.com', 'region': 'fs-upload.com',
                'upload_id': 'fs-upload.com', 'store': {'location': 's3'}, 'part': 1, 'size': 1234
            },
        )
    ]
    put_mock.assert_called_once_with(
        'http://upload.url',
        data=ANY,
        headers={'upload': 'headers'}
    )


@patch('filestack.uploads.intelligent_ingestion.requests.put')
@patch('filestack.uploads.intelligent_ingestion.requests.post')
def test_upload_part_with_resize(post_mock, put_mock):
    # this mock will work fine for commit request too
    post_mock.return_value = DummyHttpResponse(
        ok=True, json_dict={'url': 'http://upload.url', 'headers': {'upload': 'headers'}}
    )

    put_mock.side_effect = [
        DummyHttpResponse(ok=False),  # fail first attempt, should split file part
        DummyHttpResponse(),  # part 1, chunk 1
        DummyHttpResponse(),  # part 1, chunk 2
    ]

    part = {'seek_point': 0, 'num': 1}
    upload_part(
        'Aaaaapikey', 'file.txt', 'tests/data/doom.mp4', 5415034, 's3', defaultdict(lambda: 'fs-upload.com'), part
    )

    assert post_mock.call_count == 4  # 3x upload, 1 commit
    # 1st attempt
    req_args, req_kwargs = post_mock.call_args_list[0]
    assert req_kwargs['json']['size'] == 5415034
    # 2nd attempt
    req_args, req_kwargs = post_mock.call_args_list[1]
    assert req_kwargs['json']['size'] == 4194304
    # 3rd attempt
    req_args, req_kwargs = post_mock.call_args_list[2]
    assert req_kwargs['json']['size'] == 1220730


@patch('filestack.uploads.intelligent_ingestion.requests.put')
@patch('filestack.uploads.intelligent_ingestion.requests.post')
def test_min_chunk_size_exception(post_mock, put_mock):
    post_mock.return_value = DummyHttpResponse(
        ok=True, json_dict={'url': 'http://upload.url', 'headers': {'upload': 'headers'}}
    )
    put_mock.return_value = DummyHttpResponse(ok=False)

    part = {'seek_point': 0, 'num': 1}
    with pytest.raises(Exception, match='Minimal chunk size failed'):
        upload_part(
            'Aaaaapikey', 'file.txt', 'tests/data/doom.mp4', 5415034, 's3', defaultdict(lambda: 'fs-upload.com'), part
        )


@patch('filestack.uploads.intelligent_ingestion.time.sleep')
@patch('filestack.uploads.intelligent_ingestion.requests.post')
@patch('filestack.uploads.intelligent_ingestion.upload_part')
def test_wait_for_complete(upload_part, post_mock, sleep_mock):
    post_mock.side_effect = [
        DummyHttpResponse(json_dict={
            'uri': 'upload-uri', 'region': 'upload-region', 'upload_id': 'upload-id',
            'location_url': 'upload-loc-url'
        }),  # start response
        DummyHttpResponse(status_code=202),
        DummyHttpResponse(status_code=202),
        DummyHttpResponse(status_code=202),
        DummyHttpResponse(status_code=200)
    ]
    security = Security({'expires': 999}, 'secret')
    upload_params = {'filename': 'new-filename.mp4', 'path': 'some/new/path'}
    upload('AAApikeyz', 'tests/data/doom.mp4', None, 's3', upload_params, security)
    assert post_mock.call_count == 5
    start_resp_args, start_resp_kwargs = post_mock.call_args_list[0]
    url = start_resp_args[0]
    request_payload = start_resp_kwargs['json']
    assert url == 'https://upload.filestackapi.com/multipart/start'
    assert request_payload['store']['path'] == 'some/new/path'
    assert request_payload['filename'] == 'new-filename.mp4'
    assert request_payload['policy'] == 'eyJleHBpcmVzIjogOTk5fQ=='
    assert request_payload['signature'] == 'c0b1b4d794f867287eedb34e477805aa7f5e1c9d1ec24fc55a085608b79e65fa'
