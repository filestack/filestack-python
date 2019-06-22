import json
import re

import filestack.models
from filestack import config

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

    # TODO - should this class have a delete() method?

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

    def _build_url(self, security=None):
        url_elements = [config.CDN_URL, self.handle or self._external_url]

        if self._transformation_tasks:
            tasks_str = '/'.join(self._transformation_tasks)
            url_elements.insert(1, tasks_str)

        if self._external_url:
            url_elements.insert(1, self.apikey)

        if security is not None:
            url_elements.insert(-1, security.as_url_string())
        return '/'.join(url_elements)

    def debug(self):
        """
        Returns a JSON object with inforamtion regarding the current transformation

        *returns* [Dict]
        """
        debug_instance = self.add_transform_task('debug', locals())
        response = utils.make_call(debug_instance.url, 'get')
        return response.json()
