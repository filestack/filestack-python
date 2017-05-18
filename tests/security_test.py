import json
import pytest

from base64 import b64decode

from filestack import security
from filestack.exceptions import SecurityError

GOOD_POLICY = {'call': ['read'], 'expiry': 154323, 'minSize': 293042}
BAD_POLICY = {'call': ['read'], 'expiry': 154323, 'minSize': '293042'}
SECRET = 'APPSECRET'


def test_bad_policy():
    pytest.raises(SecurityError, security, BAD_POLICY, SECRET)


def test_good_policy_json():
    policy = security(GOOD_POLICY, SECRET)
    assert policy['policy']
    assert policy['signature']


def test_correct_encoding():
    policy = security(GOOD_POLICY, SECRET)
    assert b64decode(policy['policy']).decode('utf-8') == json.dumps(GOOD_POLICY)
