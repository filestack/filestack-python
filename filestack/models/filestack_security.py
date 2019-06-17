import base64
import hashlib
import hmac
import json


class Security:
    def __init__(self, policy, secret):
        self.policy = policy
        self.secret = secret
        self.policy_b64 = base64.urlsafe_b64encode(json.dumps(policy).encode('utf-8')).decode('utf-8')
        self.signature = hmac.new(
            secret.encode('utf-8'), self.policy_b64.encode('utf-8'), hashlib.sha256
        ).hexdigest()

    def as_url_string(self):
        return 'security=p:{},s:{}'.format(self.policy_b64, self.signature)


# TODO - is this needed?
# def validate(policy):
#     """
#     Validates a policy and its parameters and raises an error if invalid
#     """
#     for param, value in policy.items():
#
#         if param not in ACCEPTED_SECURITY_TYPES.keys():
#             raise SecurityError('Invalid Security Parameter: {}'.format(param))
#
#         if type(value) != ACCEPTED_SECURITY_TYPES[param]:
#             raise SecurityError('Invalid Parameter Data Type for {}, '
#                                 'Expecting: {} Received: {}'.format(
#                                     param, ACCEPTED_SECURITY_TYPES[param],
#                                     type(value)))
