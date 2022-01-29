import json

import pytest
import responses

from filestack.uploads.external_url import upload_external_url

url = 'http://image.url'
apikey = 'TESTAPIKEY'
PROCESS_URL = 'https://cdn.filestackcontent.com/process'


@pytest.mark.parametrize('default_storage, store_params, security, expected_store_tasks', [
    (
        'S3,',
        {'location': 'gcs'},
        None,
        [
            {
                'name': 'store', 'params': {'location': 'gcs'}
            }
        ]
    ),
    (
        'gcs',
        {'path': 'new-path/', 'mimetype': 'application/json'},
        type('SecurityMock', (), {'policy_b64': 'abc', 'signature': '123'}),
        [
            {
                'name': 'store', 'params': {'path': 'new-path/', 'location': 'gcs'}
            },
            {
                'name': 'security', 'params': {'policy': 'abc', 'signature': '123'}
            }
        ]
    )
])
@responses.activate
def test_upload_with_store_params(default_storage, store_params, security, expected_store_tasks):
    expected_payload = {
        'apikey': 'TESTAPIKEY',
        'sources': ['http://image.url'],
        'tasks': expected_store_tasks
    }
    responses.add(responses.POST, PROCESS_URL, json={'handle': 'newHandle'})
    upload_response = upload_external_url(
        url, apikey, default_storage, store_params=store_params, security=security
    )
    assert upload_response['handle'] == 'newHandle'
    req_payload = json.loads(responses.calls[0].request.body.decode())
    assert req_payload == expected_payload
