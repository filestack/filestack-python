from __future__ import print_function

import unittest2
import json
from base64 import b64decode

try:
    from filestack import Client, Filelink, security
    from filestack.exceptions import PolicyError
except ImportError as e:
    print(e)


class ClientTest(unittest2.TestCase):

    def setUp(self):
        self.apikey = 'APIKEY'
        self.client = Client(self.apikey)

    def test_api_set(self):
        self.assertEqual(self.apikey, self.client.apikey)


class FilelinkTest(unittest2.TestCase):

    def setUp(self):
        self.FILESTACK_CDN_URL = 'https://cdn.filestackcontent.com/'
        self.apikey = 'APIKEY'
        self.handle = 'FILEHANDLE'
        self.filelink = Filelink(self.handle, apikey=self.apikey)

    def test_handle(self):
        self.assertEqual(self.filelink.handle, self.handle)

    def test_apikey_default(self):
        filelink_default = Filelink(self.handle)
        self.assertIsNone(filelink_default.apikey)

    def test_api_get(self):
        self.assertEqual(self.apikey, self.filelink.apikey)

    def test_api_set(self):
        new_apikey = 'ANOTHER_APIKEY'
        self.filelink.apikey = new_apikey
        self.assertEqual(new_apikey, self.filelink.apikey)

    def test_url(self):
        url = self.FILESTACK_CDN_URL + self.handle
        self.assertEqual(url, self.filelink.url)


class SecurityTest(unittest2.TestCase):

    def setUp(self):
        self.good_policy = {'call': ['read'], 'expiry': 154323, 'minSize': 293042}
        self.bad_policy = {'call': ['read'], 'expiry': 154323, 'minSize': '293042'}
        self.secret = 'APPSECRET'

    def test_bad_policy(self):
        self.assertRaises(PolicyError, security, self.bad_policy, self.secret)

    def test_good_policy_json(self):
        policy = security(self.good_policy, self.secret)
        self.assertTrue(policy['policy'])
        self.assertTrue(policy['signature'])

    def test_correct_encoding(self):
        policy = security(self.good_policy, self.secret)
        self.assertEqual(b64decode(policy['policy']), json.dumps(self.good_policy))


if __name__ == '__main__':
    unittest2.main()
