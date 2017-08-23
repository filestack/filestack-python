import re

import filestack.models

from filestack.utils import utils


class AudioVisual:

    def __init__(self, url, uuid, timestamp, apikey=None, security=None):
        """
        AudioVisual instances provide a bridge between transform and filelinks, and allow
        you to check the status of a conversion and convert to a Filelink once completed

        ```python
        from filestack import Client

        client = Client("<API_KEY>")
        filelink = client.upload(filepath='path/to/file/doom.mp4')
        av_convert= filelink.av_convert(width=100, height=100)
        while av_convert.status != 'completed':
            print(av_convert.status)

        filelink = av_convert.to_filelink()
        print(filelink.url)
        ```
        """
        self._url = url
        self._apikey = apikey
        self._security = security
        self._uuid = uuid
        self._timestamp = timestamp

    def to_filelink(self):
        """
        Checks is the status of the conversion is complete and, if so, converts to a Filelink

        *returns* [Filestack.Filelink]

        ```python
        filelink = av_convert.to_filelink()
        ```
        """
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
        """
        Returns the status of the AV conversion (makes a GET request)

        *returns* [String]

        ```python
        av_convert= filelink.av_convert(width=100, height=100)
        while av_convert.status != 'completed':
            print(av_convert.status)
        ```
        """
        response = utils.make_call(self.url, 'get')
        return response.json()['status']

    @property
    def url(self):
        return self._url

    @property
    def apikey(self):
        """
        Returns the handle associated with the instance (if any)

        *returns* [String]

        ```python
        av.handle
        # YOUR_HANDLE
        ```
        """
        return self._apikey

    @property
    def security(self):
        """
        Returns the security object associated with the instance (if any)

        *returns* [Dict]

        ```python
        av.security
        # {'policy': 'YOUR_ENCODED_POLICY', 'signature': 'YOUR_ENCODED_SIGNATURE'}
        ```
        """

        return self._security

    @property
    def uuid(self):
        return self._uuid

    @property
    def timestamp(self):
        return self._timestamp
