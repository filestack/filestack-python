import re
from unittest.mock import patch

import pytest

from tests.helpers import DummyHttpResponse
from filestack import __version__
from filestack.utils import requests

TEST_URL = 'http://just.some.url'


@patch('filestack.utils.original_requests.post')
def test_req_wrapper_overwrite_headers(post_mock):
    requests.post(TEST_URL)
    post_args, post_kwargs = post_mock.call_args
    headers_sent = post_kwargs['headers']
    assert post_args[0] == TEST_URL
    assert headers_sent['User-Agent'] == 'filestack-python {}'.format(__version__)
    assert headers_sent['Filestack-Source'] == 'Python-{}'.format(__version__)
    assert re.match(r'\d+-[a-zA-Z0-9]{10}', headers_sent['Filestack-Trace-Id'])
    assert re.match(r'pythonsdk-[a-zA-Z0-9]{10}', headers_sent['Filestack-Trace-Span'])


@patch('filestack.utils.original_requests.post')
def test_req_wrapper_use_provided_headers(post_mock):
    custom_headers = {'something': 'used explicitly'}
    requests.post(TEST_URL, headers=custom_headers)
    post_args, post_kwargs = post_mock.call_args
    assert post_args[0] == TEST_URL
    assert post_kwargs['headers'] == custom_headers


@patch('filestack.utils.original_requests.post')
def test_req_wrapper_raise_exception(post_mock):
    post_mock.return_value = DummyHttpResponse(ok=False, content=b'oops!')
    with pytest.raises(Exception, match='oops!'):
        requests.post(TEST_URL)
