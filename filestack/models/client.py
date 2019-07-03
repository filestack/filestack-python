import filestack.models
from filestack import config
from filestack.uploads.external_url import upload_external_url
from filestack.trafarets import STORE_LOCATION_SCHEMA, STORE_SCHEMA
from filestack import utils
from filestack.utils import requests
from filestack.uploads import intelligent_ingestion
from filestack.uploads.multipart import multipart_upload


class Client:
    """
    The hub for all Filestack operations. Creates Filelinks, converts external urls
    to Transformation objects, takes a URL screenshot and returns zipped files.
    """
    def __init__(self, apikey, security=None, storage='S3'):
        self.apikey = apikey
        self.security = security
        STORE_LOCATION_SCHEMA.check(storage)
        self.storage = storage

    def transform_external(self, external_url):
        """
        Turns an external URL into a Filestack Transformation object

        *returns* [Filestack.Transformation]

        ```python
        from filestack import Client, Filelink

        client = Client("API_KEY")
        transform = client.transform_external('http://www.example.com')
        ```
        """
        return filestack.models.Transformation(apikey=self.apikey, security=self.security, external_url=external_url)

    def urlscreenshot(self, external_url, agent=None, mode=None, width=None, height=None, delay=None):
        """
        Takes a 'screenshot' of the given URL

        *returns* [Filestack.Transformation]

        ```python
        from filestack import Client

        client = Client("API_KEY")
        # returns a Transformation object
        screenshot = client.url_screenshot('https://www.example.com', width=100, height=100, agent="desktop")
        filelink = screenshot.store()
        ````
        """
        params = locals()
        params.pop('self')
        params.pop('external_url')

        params = {k: v for k, v in params.items() if v is not None}

        url_task = utils.return_transform_task('urlscreenshot', params)

        new_transform = filestack.models.Transformation(
            self.apikey, security=self.security, external_url=external_url
        )
        new_transform._transformation_tasks.append(url_task)

        return new_transform

    def zip(self, destination_path, file_handles, security=None):
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
        url_parts = [config.CDN_URL, self.apikey, 'zip', '[{}]'.format(','.join(file_handles))]
        sec = security or self.security
        if sec is not None:
            url_parts.insert(3, sec.as_url_string())
        zip_url = '/'.join(url_parts)
        total_bytes = 0
        with open(destination_path, 'wb') as f:
            response = requests.get(zip_url, stream=True)
            for chunk in response.iter_content(5 * 1024 ** 2):
                f.write(chunk)
                total_bytes += len(chunk)

        return total_bytes

    def upload_url(self, url, store_params=None, security=None):
        handle = upload_external_url(url, self.apikey, store_params, security=security or self.security)
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