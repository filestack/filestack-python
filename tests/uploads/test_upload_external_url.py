from unittest.mock import patch

import pytest

from tests.helpers import DummyHttpResponse
from filestack import config
from filestack.uploads.external_url import upload_external_url

url = 'http://image.url'
apikey = 'TESTAPIKEY'


@pytest.mark.parametrize('store_params, security, expected_store_tasks', [
    (
        {'location': 's3'},
        None,
        [
            {
                'name': 'store', 'params': {'location': 's3'}
            }
        ]
    ),
    (
        {'path': 'new-path/', 'mimetype': 'application/json'},
        type('SecurityMock', (), {'policy_b64': 'abc', 'signature': '123'}),
        [
            {
                'name': 'store', 'params': {'path': 'new-path/'}
            },
            {
                'name': 'security', 'params': {'policy': 'abc', 'signature': '123'}
            }
        ]
    )
])
@patch('filestack.uploads.external_url.requests.post')
def test_upload_with_store_params(post_mock, store_params, security, expected_store_tasks):
    expected_payload = {
        'apikey': 'TESTAPIKEY',
        'sources': ['http://image.url'],
        'tasks': expected_store_tasks
    }
    post_mock.return_value = DummyHttpResponse(json_dict={'handle': 'newHandle'})

    upload_response = upload_external_url(url, apikey, store_params=store_params, security=security)
    assert upload_response['handle'] == 'newHandle'
    post_args, _ = post_mock.call_args
    post_mock.assert_called_once_with('{}/process'.format(config.CDN_URL), json=expected_payload)
