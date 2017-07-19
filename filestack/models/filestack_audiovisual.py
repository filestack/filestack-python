import re

import filestack.models

from filestack.utils import utils


class AudioVisual:

    def __init__(self, url, uuid, timestamp, apikey=None, security=None):
        self._url = url
        self._apikey = apikey
        self._security = security
        self._uuid = uuid
        self._timestamp = timestamp

    def to_filelink(self):
        if self.status != 'completed':
            return 'Audio/video conversion not complete!'

        response = utils.make_call(self.url, 'get')

        if response.ok:
            response = response.json()
            handle = re.match(
                r'(?:https:\/\/cdn\.filestackcontent\.com\/)(\w+)',
                response['data']['url']
            ).group(1)
            return filestack.models.Filelink(handle, apikey=self.apikey, security=self.security)

        raise Exception(response.text)

    @property
    def status(self):
        response = utils.make_call(self.url, 'get')
        return response.json()['status']

    @property
    def url(self):
        return self._url

    @property
    def apikey(self):
        return self._apikey

    @property
    def security(self):
        return self._security

    @property
    def uuid(self):
        return self._uuid

    @property
    def timestamp(self):
        return self._timestamp
