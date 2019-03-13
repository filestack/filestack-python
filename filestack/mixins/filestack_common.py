import mimetypes
import os

import filestack.models

from filestack.config import CDN_URL, API_URL, FILE_PATH
from filestack.trafarets import CONTENT_DOWNLOAD_SCHEMA, OVERWRITE_SCHEMA
from filestack.utils import utils


class CommonMixin(object):
    """
    Contains all functions related to the manipulation of Filelinks
    """
    def download(self, destination_path, params=None):
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
        if params:
            CONTENT_DOWNLOAD_SCHEMA.check(params)
        with open(destination_path, 'wb') as new_file:
            response = utils.make_call(CDN_URL, 'get',
                                       handle=self.handle,
                                       params=params,
                                       security=self.security,
                                       transform_url=(self.url if isinstance(self, filestack.models.Transform) else None))

            if response.ok:
                for chunk in response.iter_content(1024):
                    if not chunk:
                        break
                    new_file.write(chunk)

            return response

    def get_content(self, params=None):
        """
        Returns the raw byte content of a given Filelink

        *returns* [Bytes]
        ```python
        from filestack import Client

        client =  Client('API_KEY')
        filelink = client.upload(filepath='/path/to/file/foo.jpg')
        byte_content = filelink.get_content()
        ```
        """
        if params:
            CONTENT_DOWNLOAD_SCHEMA.check(params)
        response = utils.make_call(CDN_URL, 'get',
                                   handle=self.handle,
                                   params=params,
                                   security=self.security,
                                   transform_url=(self.url if isinstance(self, filestack.models.Transform) else None))

        return response.content

    def get_metadata(self, params=None):
        """
        Metadata provides certain information about a Filehandle, and you can specify which pieces
        of information you will receive back by passing in optional parameters.

        ```python
        from filestack import Client

        client =  Client('API_KEY')
        filelink = client.upload(filepath='/path/to/file/foo.jpg')
        metadata = filelink.get_metadata()
        # or define specific metadata to receive
        metadata = filelink.get_metadata({'filename': true})
        ```
        """
        metadata_url = "{CDN_URL}/{handle}/metadata".format(
            CDN_URL=CDN_URL, handle=self.handle
        )
        response = utils.make_call(metadata_url, 'get',
                                   params=params,
                                   security=self.security)
        return response.json()

    def delete(self, params=None):
        """
        You may delete any file you have uploaded, either through a Filelink returned from the client or one you have initialized yourself.
        This returns a response of success or failure. This action requires security.abs

        *returns* [requests.response]

        ```python
        from filestack import Client, security

        # a policy requires at least an expiry
        policy = {'expiry': 56589012}
        sec = security(policy, 'APP_SECRET')

        client =  Client('API_KEY', security=sec)
        filelink = client.upload(filepath='/path/to/file/foo.txt')
        response = filelink.delete()
        ```
        """
        if params:
            params['key'] = self.apikey
        else:
            params = {'key': self.apikey}
        return utils.make_call(API_URL, 'delete',
                               path=FILE_PATH,
                               handle=self.handle,
                               params=params,
                               security=self.security,
                               transform_url=self.url if isinstance(self, filestack.models.Transform) else None)

    def overwrite(self, url=None, filepath=None, params=None):
        """
        You may overwrite any Filelink by supplying a new file. The Filehandle will remain the same.

        *returns* [requests.response]

        ```python
        from filestack import Client, security

        # a policy requires at least an expiry
        policy = {'expiry': 56589012}
        sec = security(policy, 'APP_SECRET')

        client =  Client('API_KEY', security=sec)
        ```
        """
        if params:
            OVERWRITE_SCHEMA.check(params)
        data, files = None, None
        if url:
            data = {'url': url}
        elif filepath:
            filename = os.path.basename(filepath)
            mimetype = mimetypes.guess_type(filepath)[0]
            files = {'fileUpload': (filename, open(filepath, 'rb'), mimetype)}
        else:
            raise ValueError("You must include a url or filepath parameter")

        return utils.make_call(API_URL, 'post',
                               path=FILE_PATH,
                               params=params,
                               handle=self.handle,
                               data=data,
                               files=files,
                               security=self.security,
                               transform_url=self.url if isinstance(self, filestack.models.Transform) else None)
