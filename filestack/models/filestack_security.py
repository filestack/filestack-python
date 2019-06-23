import base64
import hashlib
import hmac
import json


class Security:
    def __init__(self, policy, secret):
        self.policy = policy
        self.secret = secret
        self.policy_b64 = base64.urlsafe_b64encode(json.dumps(policy, sort_keys=True).encode('utf-8')).decode('utf-8')
        self.signature = hmac.new(
            secret.encode('utf-8'), self.policy_b64.encode('utf-8'), hashlib.sha256
        ).hexdigest()

    def as_url_string(self):
        return 'security=p:{},s:{}'.format(self.policy_b64, self.signature)
