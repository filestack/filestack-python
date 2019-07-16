import pytest
from filestack.helpers import verify_webhook_signature


@pytest.mark.parametrize('signature, expected_result', [
    ('57cbb25386c3d6ff758a7a75cf52ba02cf2b0a1a2d6d5dfb9c886553ca6011cb', True),
    ('incorrect-signature', False),
])
def test_webhook_verification(signature, expected_result):
    secret = 'webhook-secret'
    body = b'{"text": {"filename": "filename.jpg", "key": "kGaeljnga9wkysK6Z_filename.jpg"}}'

    headers = {
        'FS-Signature': signature,
        'FS-Timestamp': 123456789999
    }
    result, details = verify_webhook_signature(secret, body, headers)
    assert result is expected_result
    if expected_result is False:
        assert 'Signature mismatch' in details['error']


@pytest.mark.parametrize('secret, body, headers, err_msg', [
    ('hook-secret', b'body', 'should be a dict', 'value is not a dict'),
    (1, b'body', {'FS-Signature': 'abc', 'FS-Timestamp': 123}, 'value is not a string'),
    ('hook-secret', b'', {'FS-Timestamp': 123}, 'fs-signature header is missing'),
    ('hook-secret', ['incorrect'], {'FS-Signature': 'abc', 'FS-Timestamp': 123}, 'Invalid webhook body'),
])
def test_agrument_validation(secret, body, headers, err_msg):
    result, details = verify_webhook_signature(secret, body, headers)
    assert result is False
    assert err_msg in details['error']
