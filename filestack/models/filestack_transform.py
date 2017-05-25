import json
import re

import filestack.models

from filestack.mixins import ImageTransformationMixin, CommonMixin
from filestack.utils import utils


class Transform(ImageTransformationMixin, CommonMixin):

    def __init__(self, apikey=None, handle=None, external_url=None, security=None):
        self._apikey = apikey
        self._handle = handle
        self._security = security
        self._external_url = external_url
        self._transformation_tasks = []

    @property
    def handle(self):
        return self._handle

    @property
    def external_url(self):
        return self._external_url

    @property
    def apikey(self):
        return self._apikey

    @property
    def security(self):
        return self._security

    @property
    def url(self):
        return utils.get_transform_url(
            self._transformation_tasks, external_url=self.external_url,
            handle=self.handle, security=self.security, apikey=self.apikey
        )

    def store(self, filename=None, location=None, path=None, container=None, region=None, access=None, base64decode=None):
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
        debug_instance = self.add_transform_task('debug', locals())
        response = utils.make_call(debug_instance.url, 'get')
        return response.json()
