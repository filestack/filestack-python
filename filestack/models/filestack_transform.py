import json
import re

import filestack.models

from filestack.mixins import ImageTransformationMixin, CommonMixin
from filestack.utils import utils


class Transform(ImageTransformationMixin, CommonMixin):
    """
    Transform objects take either a handle or an external URL. They act similarly to
    Filelinks, but have specific methods like store, debug, and also construct
    URLs differently.

    Transform objects can be chained to build up multi-task transform URLs, each one saved in
    self._transformation_tasks
    """

    def __init__(self, apikey=None, handle=None, external_url=None, security=None):
        """
        ```python
        from filestack import Client

        client = Client("<API_KEY>")
        filelink = client.upload(filepath='/path/to/file/foo.jpg')
        transform = filelink.resize(width=100, height=100).rotate(deg=90)

        new_filelink = transform.store()
        ```
        """
        self._apikey = apikey
        self._handle = handle
        self._security = security
        self._external_url = external_url
        self._transformation_tasks = []

    @property
    def handle(self):
        """
        Returns the handle associated with the instance (if any)

        *returns* [String]

        ```python
        transform.handle
        # YOUR_HANDLE
        ```
        """
        return self._handle

    @property
    def external_url(self):
        """
        Returns the external URL associated with the instance (if any)

        *returns* [String]

        ```python
        transform.external_url
        # YOUR_EXTERNAL_URL
        ```
        """
        return self._external_url

    @property
    def apikey(self):
        """
        Returns the API key associated with the instance

        *returns* [String]

        ```python
        transform.apikey
        # YOUR_API_KEY
        ```
        """
        return self._apikey

    @property
    def security(self):
        """
        Returns the security object associated with the instance (if any)

        *returns* [Dict]

        ```python
        transform.security
        # {'policy': 'YOUR_ENCODED_POLICY', 'signature': 'YOUR_ENCODED_SIGNATURE'}
        ```
        """

        return self._security

    @property
    def url(self):
        """
        Returns the URL for the current transformation, which can be used
        to retrieve the file. If security is enabled, signature and policy parameters will
        be included

        *returns* [String]

        ```python
        transform = client.upload(filepath='/path/to/file')
        transform.url()
        # https://cdn.filestackcontent.com/TRANSFORMS/FILE_HANDLE
        ```
        """
        return utils.get_transform_url(
            self._transformation_tasks, external_url=self.external_url,
            handle=self.handle, security=self.security, apikey=self.apikey
        )

    def store(self, filename=None, location=None, path=None, container=None, region=None, access=None, base64decode=None):
        """
        Uploads and stores the current transformation as a Fileink

        *returns* [Filestack.Filelink]

        ```python
        filelink = transform.store()
        ```
        """
        if path:
            path = '"{}"'.format(path)

        filelink_obj = self.add_transform_task('store', locals())
        response = utils.make_call(filelink_obj.url, 'get')

        if response.ok:
            data = json.loads(response.text)
            handle = re.match(r'(?:https:\/\/cdn\.filestackcontent\.com\/)(\w+)', data['url']).group(1)
            return filestack.models.Filelink(handle, apikey=self.apikey, security=self.security)
        else:
            raise Exception(response.text)

    def debug(self):
        """
        Returns a JSON object with inforamtion regarding the current transformation

        *returns* [Dict]
        """
        debug_instance = self.add_transform_task('debug', locals())
        response = utils.make_call(debug_instance.url, 'get')
        return response.json()
