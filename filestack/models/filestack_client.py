import os
import re
import hmac
import json
import hashlib
import requests
import mimetypes

import filestack.models

from filestack.config import API_URL, CDN_URL, STORE_PATH, HEADERS
from filestack.trafarets import STORE_LOCATION_SCHEMA, STORE_SCHEMA
from filestack.utils import utils, upload_utils, intelligent_ingestion


class Client:
    """
    The hub for all Filestack operations. Creates Filelinks, converts external to transform objects,
    takes a URL screenshot and returns zipped files.
    """
    def __init__(self, apikey, security=None, storage='S3'):
        self._apikey = apikey
        self._security = security
        STORE_LOCATION_SCHEMA.check(storage)
        self._storage = storage

    def transform_external(self, external_url):
        """
        Turns an external URL into a Filestack Transform object

        *returns* [Filestack.Transform]

        ```python
        from filestack import Client, Filelink

        client = Client("API_KEY")
        transform = client.transform_external('http://www.example.com')
        ```
        """
        return filestack.models.Transform(apikey=self.apikey, security=self.security, external_url=external_url)

    def urlscreenshot(self, external_url, agent=None, mode=None, width=None, height=None, delay=None):
        """
        Takes a 'screenshot' of the given URL

        *returns* [Filestack.Transform]

        ```python
        from filestack import Client

        client = Client("API_KEY")
        # returns a Transform object
        screenshot = client.url_screenshot('https://www.example.com', width=100, height=100, agent="desktop")
        filelink = screenshot.store()
        ````
        """
        params = locals()
        params.pop('self')
        params.pop('external_url')

        params = {k: v for k, v in params.items() if v is not None}

        url_task = utils.return_transform_task('urlscreenshot', params)

        new_transform = filestack.models.Transform(apikey=self.apikey, security=self.security, external_url=external_url)
        new_transform._transformation_tasks.append(url_task)

        return new_transform

    def zip(self, destination_path, files):
        """
        Takes array of files and downloads a compressed ZIP archive
        to provided path

        *returns* [requests.response]

        ```python
        from filestack import Client

        client = Client("<API_KEY>")
        client.zip('/path/to/file/destination', ['files'])
        ```
        """
        zip_url = "{}/{}/zip/[{}]".format(CDN_URL, self.apikey, ','.join(files))
        with open(destination_path, 'wb') as new_file:
            response = utils.make_call(zip_url, 'get')
            if response.ok:
                for chunk in response.iter_content(1024):
                    if not chunk:
                        break
                    new_file.write(chunk)

                return response

            return response.text

    def upload(self, url=None, filepath=None, multipart=True, params=None, upload_processes=None, intelligent=False):
        """
        Uploads a file either through a local filepath or external_url.
        Uses multipart by default and Intelligent Ingestion by default (if enabled).
        You can specify the number of multipart processes and pass in parameters.

        returns [Filestack.Filelink]
        ```python
        from filestack import Client

        client = Client("<API_KEY>")
        filelink = client.upload(filepath='/path/to/file')

        # to use different storage:
        client = FilestackClient.new('API_KEY', storage='dropbox')
        filelink = client.upload(filepath='/path/to/file', params={'container': 'my-container'})

        # to use an external URL:
        filelink = client.upload(external_url='https://www.example.com')

        # to disable intelligent ingestion:
        filelink = client.upload(filepath='/path/to/file', intelligent=False)
        ```
        """

        if params:  # Check the structure of parameters
            STORE_SCHEMA.check(params)

        if filepath and url:  # Raise an error for using both filepath and external url
            raise ValueError("Cannot upload file and external url at the same time")

        if filepath:  # Uploading from local drive
            if intelligent:
                response = intelligent_ingestion.upload(
                    self.apikey, filepath, self.storage, params=params, security=self.security
                )

            elif multipart:
                response = upload_utils.multipart_upload(
                    self.apikey, filepath, self.storage,
                    upload_processes=upload_processes, params=params, security=self.security
                )
                handle = response['handle']
                return filestack.models.Filelink(handle, apikey=self.apikey, security=self.security)

            else:  # Uploading with multipart=False
                filename = os.path.basename(filepath)
                mimetype = mimetypes.guess_type(filepath)[0]
                files = {'fileUpload': (filename, open(filepath, 'rb'), mimetype)}

                if params:
                    params['key'] = self.apikey
                else:
                    params = {'key': self.apikey}

                path = '{path}/{storage}'.format(path=STORE_PATH, storage=self.storage)

                if self.security:
                    path = "{path}?policy={policy}&signature={signature}".format(
                        path=path, policy=self.security['policy'].decode('utf-8'),
                        signature=self.security['signature']
                    )

                response = utils.make_call(
                    API_URL, 'post', path=path, params=params, files=files
                )

        else:  # Uploading from an external URL
            tasks = []
            request_url_list = []

            if utils.store_params_checker(params):
                store_task = utils.store_params_maker(params)
                tasks.append(store_task)

            if self.security:
                tasks.append(
                    'security=p:{policy},s:{signature}'.format(
                        policy=self.security['policy'].decode('utf-8'),
                        signature=self.security['signature']
                    )
                )

            tasks = '/'.join(tasks)

            if tasks:
                request_url_list.extend((CDN_URL, self.apikey, tasks, url))
            else:
                request_url_list.extend((CDN_URL, self.apikey, url))

            request_url = '/'.join(request_url_list)

            response = requests.post(request_url, headers=HEADERS)

        if response.ok:
            response = response.json()
            handle = re.match(
                r'(?:https:\/\/cdn\.filestackcontent\.com\/)(\w+)',
                response['url']
            ).group(1)
            return filestack.models.Filelink(handle, apikey=self.apikey, security=self.security)
        else:
            raise Exception('Invalid API response')

    @staticmethod
    def verify_webhook_signature(secret, body, headers=None):
        """
        Checks if webhook, which you received was originally from Filestack,
        based on you secret for webhook endpoint which was generated in Filestack developer portal.
        Body suppose to be raw content of received webhook

        returns [Dict]
        ```python
        from filestack import Client

        result = client.validate_webhook_signature(
            'secret', b'{"webhook_content": "received_from_filestack"}',
            {'FS-Timestamp': '1558367878', 'FS-Signature': 'Filestack Signature'}
        )
        ```
        Response will contain keys 'error' and 'valid'.
        If 'error' is not None - it means that you provided wrong parameters
        If 'valid' is False - it means that signature is invalid and probably Filestack is not source of webhook
        """
        error = Client.validate_webhook_params(secret, body, headers)

        if error:
            return {'error': error, 'valid': True}

        error, headers_prepared = Client.prepare_and_validate_webhook_headers(headers)

        if error:
            return {'error': error, 'valid': True}

        if isinstance(body, bytes):
            body = body.decode('latin-1')

        sign = "%s.%s" % (headers_prepared['fs-timestamp'], body)
        signature = hmac.new(secret.encode('latin-1'), sign.encode('latin-1'), hashlib.sha256).hexdigest()

        return {'error': None, 'valid': signature == headers_prepared['fs-signature']}

    @staticmethod
    def validate_webhook_params(secret, body, headers):
        error = None
        if not secret or not isinstance(secret, str):
            error = 'Missing secret or secret is not a string'
        if not headers or not isinstance(headers, dict):
            error = 'Missing headers or headers are not a dict'
        if not body or not isinstance(body, (str, bytes)):
            error = 'Missing content or content is not string/bytes type'
        return error

    @staticmethod
    def prepare_and_validate_webhook_headers(headers):
        error = None
        headers_prepared = dict((k.lower(), v) for k, v in headers.items())
        if 'fs-signature' not in headers_prepared:
            error = 'Missing `Signature` value in provided headers'
        if 'fs-timestamp' not in headers_prepared:
            error = 'Missing `Timestamp` value in provided headers'
        return error, headers_prepared

    @property
    def security(self):
        """
        Returns the security object associated with the instance (if any)

        *returns* [Dict]

        ```python
        client.security
        # {'policy': 'YOUR_ENCODED_POLICY', 'signature': 'YOUR_ENCODED_SIGNATURE'}
        ```
        """
        return self._security

    @property
    def storage(self):
        """
        Returns the storage associated with the client (defaults to 'S3')

        *returns* [Dict]

        ```python
        client.storage
        # S3
        ```
        """
        return self._storage

    @property
    def apikey(self):
        """
        Returns the API key associated with the instance

        *returns* [String]

        ```python
        client.apikey
        # YOUR_API_KEY
        ```
        """
        return self._apikey
