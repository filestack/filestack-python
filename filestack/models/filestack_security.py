from filestack.config import ACCEPTED_SECURITY_TYPES
from filestack.exceptions import SecurityError

import base64
import hashlib
import hmac
import json


def validate(policy):
    """
    Validates a policy and its parameters and raises an error if invalid
    """
    for param, value in policy.items():

        if param not in ACCEPTED_SECURITY_TYPES.keys():
            raise SecurityError('Invalid Security Parameter: {}'.format(param))

        if type(value) != ACCEPTED_SECURITY_TYPES[param]:
            raise SecurityError('Invalid Parameter Data Type for {}, '
                                'Expecting: {} Received: {}'.format(
                                    param, ACCEPTED_SECURITY_TYPES[param],
                                    type(value)))


def security(policy, app_secret):
    """
    Creates a valid signature and policy based on provided app secret and
    parameters
    ```python
    from filestack import Client, security

    # a policy requires at least an expiry
    policy = {'expiry': 56589012, 'call': ['read', 'store', 'pick']}
    sec = security(policy, 'APP_SECRET')

    client =  Client('API_KEY', security=sec)
    ```
    """
    validate(policy)
    policy_enc = base64.urlsafe_b64encode(json.dumps(policy).encode('utf-8'))

    signature = hmac.new(app_secret.encode('utf-8'),
                         policy_enc,
                         hashlib.sha256).hexdigest()

    return {'policy': policy_enc, 'signature': signature}
