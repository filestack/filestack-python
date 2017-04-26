from __future__ import print_function

import unittest2

try:
    from filestack import Client, Filelink
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
        self.apikey = 'APIKEY'
        self.filelink = Filelink(apikey=self.apikey)

    def test_apikey_default(self):
        filelink_default = Filelink()
        self.assertIsNone(filelink_default.apikey)

    def test_api_get(self):
        self.assertEqual(self.apikey, self.filelink.apikey)

    def test_api_set(self):
        new_apikey = 'ANOTHER_APIKEY'
        self.filelink.apikey = new_apikey
        self.assertEqual(new_apikey, self.filelink.apikey)


if __name__ == '__main__':
    unittest2.main()
