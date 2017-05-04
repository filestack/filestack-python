import json
import base64
import hmac
import hashlib
from filestack.config import ACCEPTED_SECURITY_TYPES
from filestack.exceptions import PolicyError


def validate(policy):
    for param, value in policy.items():

        if param not in ACCEPTED_SECURITY_TYPES.keys():
            raise PolicyError('Invalid Security Parameter: {}'.format(param))

        if type(value) != ACCEPTED_SECURITY_TYPES[param]:
            raise PolicyError('Invalid Parameter Data Type for {}, '
                              'Expecting: {} Received: {}'.format(
                                param, ACCEPTED_SECURITY_TYPES[param],
                                type(value)))


def security(policy, app_secret):
    validate(policy)
    policy_enc = base64.urlsafe_b64encode(json.dumps(policy).encode('utf-8'))

    signature = hmac.new(app_secret.encode('utf-8'),
                         policy_enc,
                         hashlib.sha256).hexdigest()

    return {'policy': policy_enc, 'signature': signature}
