import mimetypes
import os

import filestack.models
from filestack.config import API_URL, FILE_PATH
from filestack.trafarets import OVERWRITE_SCHEMA
from filestack import utils
from filestack.utils import requests


class CommonMixin(object):
    """
    Contains all functions related to the manipulation of Filelinks
    """

    @property
    def url(self):
        """
        Returns object's URL

        *returns* [String]

        ```python
        filelink = client.upload(filepath='/path/to/file')
        filelink.url
        # https://cdn.filestackcontent.com/FILE_HANDLE
        ```
        """
        return self._build_url()

    def signed_url(self, security=None):
        sec = security or self.security
        if sec is None:
            raise ValueError('Security is required to sign url')
        return self._build_url(security=sec)

    def store(self, filename=None, location=None, path=None, container=None,
              region=None, access=None, base64decode=None, workflows=None):
        instance = self.add_transform_task('store', locals())
        response = requests.post(instance.url)
        return filestack.models.Filelink(handle=response.json()['handle'])

    def download(self, destination_path, security=None):
        """
        Downloads a file to the given local path and returns the size of the downloaded file if successful

        *returns* [Integer]

        ```python
        from filestack import Client

        client =  Client('API_KEY', security=sec)
        filelink = client.upload(filepath='/path/to/file')
        # if successful, returns size of downloaded file in bytes
        response = filelink.download('path/to/file')
        ```
        """
        sec = security or self.security
        total_bytes = 0

        with open(destination_path, 'wb') as f:
            response = requests.get(self._build_url(security=sec), stream=True)
            for data_chunk in response.iter_content(5 * 1024 ** 2):
                f.write(data_chunk)
                total_bytes += len(data_chunk)

        return total_bytes

    def get_content(self, security=None):
        """
        Returns the raw byte content of a given object

        *returns* [Bytes]
        ```python
        from filestack import Client

        client =  Client('API_KEY')
        filelink = client.upload(filepath='/path/to/file/foo.jpg')
        byte_content = filelink.get_content()
        ```
        """
        sec = security or self.security
        response = requests.get(self._build_url(security=sec))
        return response.content

    def tags(self, security=None):
        obj = self.add_transform_task('tags', params={'self': None})
        response = requests.get(obj.signed_url(security=security))
        return response.json()

    def sfw(self, security=None):
        obj = self.add_transform_task('sfw', params={'self': None})
        response = requests.get(obj.signed_url(security=security))
        return response.json()
