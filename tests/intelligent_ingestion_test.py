from mock import patch, call, ANY
from collections import defaultdict

import pytest

from filestack import __version__
from filestack.utils.intelligent_ingestion import upload_part, filestack_request, upload


class DummyHttpResponse:
    def __init__(self, ok=True, json_dict=None, headers=None, status_code=200, text=''):
        self.ok = ok
        self.json_dict = json_dict or {}
        self.headers = headers or {}
        self.status_code = status_code
        self.content = b''
        self.text = text

    def json(self):
        return self.json_dict


@patch('filestack.utils.intelligent_ingestion.requests.post')
def test_filestack_request_success(post_mock):
    post_mock.return_value = DummyHttpResponse(json_dict={'a': 1})
    response = filestack_request('http://req.url', {})
    assert response.json() == {'a': 1}


@patch('filestack.utils.intelligent_ingestion.requests.post')
def test_filestack_request_error(post_mock):
    post_mock.return_value = DummyHttpResponse(ok=False, text='Invalid Filestack API response')
    with pytest.raises(Exception, match='Invalid Filestack API response'):
        filestack_request('http://req.url', {})


@patch('filestack.utils.intelligent_ingestion.requests.put')
@patch('filestack.utils.intelligent_ingestion.requests.post')
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
            headers={'User-Agent': 'filestack-python {}'.format(__version__), 'Filestack-Source': 'Python-{}'.format(__version__)}
        ),
        call(
            'https://fs-upload.com/multipart/commit',
            json={
                'apikey': 'Aaaaapikey', 'uri': 'fs-upload.com', 'region': 'fs-upload.com',
                'upload_id': 'fs-upload.com', 'store': {'location': 's3'}, 'part': 1, 'size': 1234
            },
            headers={'User-Agent': 'filestack-python {}'.format(__version__), 'Filestack-Source': 'Python-{}'.format(__version__)}
        )
    ]
    put_mock.assert_called_once_with(
        'http://upload.url',
        data=ANY,
        headers={'upload': 'headers'}
    )


@patch('filestack.utils.intelligent_ingestion.requests.put')
@patch('filestack.utils.intelligent_ingestion.requests.post')
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


@patch('filestack.utils.intelligent_ingestion.requests.put')
@patch('filestack.utils.intelligent_ingestion.requests.post')
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


@patch('filestack.utils.intelligent_ingestion.time.sleep')
@patch('filestack.utils.intelligent_ingestion.requests.post')
@patch('filestack.utils.intelligent_ingestion.upload_part')
@patch('filestack.utils.intelligent_ingestion.filestack_request')
def test_wait_for_complete(fs_request, upload_part, post_mock, sleep_mock):
    post_mock.side_effect = [
        DummyHttpResponse(status_code=202),
        DummyHttpResponse(status_code=202),
        DummyHttpResponse(status_code=202),
        DummyHttpResponse(status_code=200)
    ]
    fs_request.return_value = DummyHttpResponse(json_dict={
        'uri': 'upload-uri', 'region': 'upload-region', 'upload_id': 'upload-id',
        'location_url': 'upload-loc-url'
    })
    security = {'policy': b'fspolicy', 'signature': 'fssignature'}
    upload_params = {'filename': 'new-filename.mp4', 'path': 'some/new/path'}
    upload('AAApikeyz', 'tests/data/doom.mp4', 's3', upload_params, security)
    assert post_mock.call_count == 4
    req_args, req_kwargs = fs_request.call_args
    url, request_data = req_args
    assert url == 'https://upload.filestackapi.com/multipart/start'
    assert request_data['store']['path'] == 'some/new/path'
    assert request_data['filename'] == 'new-filename.mp4'
    assert request_data['policy'] == 'fspolicy'
    assert request_data['signature'] == 'fssignature'
