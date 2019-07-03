import hmac
import hashlib

import trafaret as t


def check_body(val):
    if isinstance(val, str) or isinstance(val, bytes):
        return val
    return t.DataError('Invalid webhook body. Expected: string or bytes')


def check_headers(headers):
    if not isinstance(headers, dict):
        return t.DataError('value is not a dict')

    headers = dict((k.lower(), v) for k, v in headers.items())
    for item in ('fs-signature', 'fs-timestamp'):
        if item.lower() not in headers:
            return t.DataError('{} header is missing'.format(item))
    return headers


VerificationArguments = t.Dict({
    'secret': t.String,
    'body': t.Call(check_body),
    'headers': t.Call(check_headers)
})


def verify_webhook_signature(secret=None, body=None, headers=None):
    """
    Checks if webhook, which you received was sent Filestack,
    based on your secret for webhook endpoint which was generated in Filestack developer portal.
    Body suppose to be raw content of received webhook

    returns [Tuple]
    ```python
    from filestack import Client

    result, details = verify_webhook_signature(
        'secret', b'{"webhook_content": "received_from_filestack"}',
        {'FS-Timestamp': '1558367878', 'FS-Signature': 'filestack-signature'}
    )
    ```
    Positive verification result: True, {}
    Negative verification result: False, {'error': 'error details'}
    """
    try:
        VerificationArguments.check({
            'secret': secret, 'body': body, 'headers': headers
        })
    except t.DataError as e:
        return False, {'error': str(e.as_dict())}

    lowercase_headers = dict((k.lower(), v) for k, v in headers.items())
    if isinstance(body, bytes):
        body = body.decode('utf-8')

    lowercase_headers = dict((k.lower(), v) for k, v in headers.items())
    hmac_data = '{}.{}'.format(lowercase_headers['fs-timestamp'], body)
    signature = hmac.new(secret.encode('utf-8'), hmac_data.encode('utf-8'), hashlib.sha256).hexdigest()
    expected = lowercase_headers['fs-signature']
    if signature != expected:
        return False, {'error': 'Signature mismatch! Expected: {}. Got: {}'.format(expected, signature)}
    return True, {}
