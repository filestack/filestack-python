import hmac
import hashlib

import requests

import filestack.models
from filestack import config
from filestack.uploads.external_url import upload_external_url
from filestack.trafarets import STORE_LOCATION_SCHEMA, STORE_SCHEMA
from filestack.utils import utils, intelligent_ingestion
from filestack.uploads.multipart import multipart_upload


class Client:
    """
    The hub for all Filestack operations. Creates Filelinks, converts external urls
    to Transform objects, takes a URL screenshot and returns zipped files.
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

        new_transform = filestack.models.Transform(self.apikey, security=self.security, external_url=external_url)
        new_transform._transformation_tasks.append(url_task)

        return new_transform

    def zip(self, destination_path, file_handles):
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
        # TODO - should this use security too?
        zip_url = '{}/{}/zip/[{}]'.format(config.CDN_URL, self.apikey, ','.join(file_handles))
        total_bytes = 0

        with open(destination_path, 'wb') as f:
            response = requests.get(zip_url, stream=True)
            if not response.ok:
                raise Exception(response.text)

            for chunk in response.iter_content(5 * 1024 ** 2):
                f.write(chunk)
                total_bytes += len(chunk)

        return total_bytes

    def upload_url(self, url, store_params=None):
        handle = upload_external_url(url, self.apikey, store_params)
        return filestack.models.Filelink(handle=handle)

    def upload(self, filepath=None, file_obj=None, store_params=None, intelligent=False):
        """
        Uploads a file either through a local filepath or external_url.

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

        if store_params:  # Check the structure of parameters
            STORE_SCHEMA.check(store_params)

        upload_method = multipart_upload
        if intelligent:
            upload_method = intelligent_ingestion.upload

        response_json = upload_method(
            self.apikey, filepath, file_obj, self.storage, params=store_params, security=self.security
        )

        handle = response_json['handle']
        return filestack.models.Filelink(handle, apikey=self.apikey, security=self.security)

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
