import base64
import hashlib
import hmac
import json


class Security:
    """
    Security objects are used to sign API calls.
    To learn more about Filestack Security, please visit https://www.filestack.com/docs/concepts/security

    >>> sec = Security({'expiry': 1562763146, 'call': ['read']}, 'SECURITY-SECRET')
    >>> sec.policy
    {'expiry': 1562763146, 'call': ['read']}
    >>> sec.policy_b64
    'eyJjYWxsIjogWyJyZWFkIl0sICJleHBpcnkiOiAxNTYyNzYzMTQ2fQ=='
    >>> sec.signature
    '89f1325dca54cfce976163fb692bb266f28129525b8c6bb0eeadf4b7d450e2f0'
    """
    def __init__(self, policy, secret):
        """
        Args:
            policy (dict): policy to be used
            secret (str): your application secret
        """
        self.policy = policy
        self.secret = secret
        self.policy_b64 = base64.urlsafe_b64encode(json.dumps(policy, sort_keys=True).encode('utf-8')).decode('utf-8')
        self.signature = hmac.new(
            secret.encode('utf-8'), self.policy_b64.encode('utf-8'), hashlib.sha256
        ).hexdigest()

    def as_url_string(self):
        """
        Returns the security part of signed urls

        Returns:
            str: url part in the form of :data:`security=p:\\<encoded policy>,s:\\<signature>`
        """
        return 'security=p:{},s:{}'.format(self.policy_b64, self.signature)
