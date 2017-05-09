from __future__ import print_function

import unittest2
import json

from base64 import b64decode
from httmock import urlmatch, HTTMock, response, all_requests
from trafaret import DataError

try:
    from filestack import Client, Filelink, security
    from filestack.exceptions import SecurityError
except ImportError as e:
    print(e)


class ClientTest(unittest2.TestCase):

    def setUp(self):
        self.apikey = 'APIKEY'
        self.client = Client(self.apikey)
        self.handle = 'SOMEHANDLE'

    def test_api_set(self):
        self.assertEqual(self.apikey, self.client.apikey)

    def test_wrong_storage(self):
        kwargs = {'apikey': self.apikey, 'storage': 'googlecloud'}
        self.assertRaises(DataError, Client, **kwargs)

    def test_store(self):
        @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/store', method='post', scheme='https')
        def api_store(url, request):
            return response(200, {'url': 'https://cdn.filestackcontent.com/{}'.format(self.handle)})

        with HTTMock(api_store):
            filelink = self.client.upload(url="someurl")

        self.assertIsInstance(filelink, Filelink)
        self.assertEqual(filelink.handle, self.handle)

    def test_wrong_store_params(self):
        kwargs = {'params': {'call': 'someparameter'}, 'url': 'someurl'}
        self.assertRaises(DataError, self.client.upload, **kwargs)

    def test_bad_store_params(self):
        kwargs = {'params': {'access': True}, 'url': 'someurl'}
        self.assertRaises(DataError, self.client.upload, **kwargs)

    def test_invalid_client_method(self):
        self.assertRaises(AttributeError, self.client.delete)

class FilelinkTest(unittest2.TestCase):

    def setUp(self):
        self.FILESTACK_CDN_URL = 'https://cdn.filestackcontent.com/'
        self.apikey = 'APIKEY'
        self.handle = 'FILEHANDLE'
        self.filelink = Filelink(self.handle, apikey=self.apikey)

        self.security = security({'call': ['read'], 'expiry': 10238239}, 'APPSECRET')
        self.secure_filelink = Filelink(self.handle, apikey=self.apikey, security=self.security)

    """ TEST INSTANTIATION """

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


    """ TEST GET CONTENT AND DOWNLOAD """

    def test_get_content(self):
        @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/file', method='get', scheme='https')
        def api_download(url, request):
            return response(200, b'SOMEBYTESCONTENT')

        with HTTMock(api_download):
            content = self.filelink.get_content()

        self.assertEqual(content, b'SOMEBYTESCONTENT')

    def test_get_content_params(self):
        @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/file', method='get', scheme='https')
        def api_download(url, request):
            return response(200, b'SOMEBYTESCONTENT')

        with HTTMock(api_download):
            content = self.filelink.get_content(params={'dl': True})

        self.assertEqual(content, b'SOMEBYTESCONTENT')

    def test_get_content_bad_params(self):
        kwargs = {'params': {'call': ['read']}}
        self.assertRaises(DataError, self.filelink.get_content, **kwargs)

    def test_get_content_bad_param_value(self):
        kwargs = {'params': {'dl': 'true'}}
        self.assertRaises(DataError, self.filelink.get_content, **kwargs)

    """ TEST DELETE """

    def test_delete_content(self):
        @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/file', method='delete', scheme='https')
        def api_delete(url, request):
            return response(200)

        with HTTMock(api_delete):
            delete_response = self.secure_filelink.delete()

        self.assertEqual(delete_response.status_code, 200)

    """ TEST OVEWRITE """

    def test_overwrite_content(self):
        @urlmatch(netloc=r'www\.filestackapi\.com', path='/api/file', method='post', scheme='https')
        def api_delete(url, request):
            return response(200, {'handle': self.handle})

        with HTTMock(api_delete):
            filelink_response = self.secure_filelink.overwrite(url="http://www.someurl.com")

        self.assertEqual(filelink_response.status_code, 200)

    def test_overwrite_argument_fail(self):
        # passing in neither the url or filepath parameter
        self.assertRaises(ValueError, self.filelink.overwrite)

    def test_overwrite_bad_params(self):
        kwargs = {'params': {'call': ['read']}}
        self.assertRaises(DataError, self.secure_filelink.overwrite, **kwargs)

    def test_overwrite_bad_param_value(self):
        kwargs = {'params': {'base64decode': 'true'}}
        self.assertRaises(DataError, self.secure_filelink.overwrite, **kwargs)


class SecurityTest(unittest2.TestCase):

    def setUp(self):
        self.good_policy = {'call': ['read'], 'expiry': 154323, 'minSize': 293042}
        self.bad_policy = {'call': ['read'], 'expiry': 154323, 'minSize': '293042'}
        self.secret = 'APPSECRET'

    def test_bad_policy(self):
        self.assertRaises(SecurityError, security, self.bad_policy, self.secret)

    def test_good_policy_json(self):
        policy = security(self.good_policy, self.secret)
        self.assertTrue(policy['policy'])
        self.assertTrue(policy['signature'])

    def test_correct_encoding(self):
        policy = security(self.good_policy, self.secret)
        self.assertEqual(b64decode(policy['policy']).decode('utf-8'), json.dumps(self.good_policy))


if __name__ == '__main__':
    unittest2.main()
