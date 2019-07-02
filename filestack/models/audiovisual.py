import filestack.models
from filestack.utils import requests


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
        self.url = url
        self.apikey = apikey
        self.security = security
        self.uuid = uuid
        self.timestamp = timestamp

    def to_filelink(self):
        """
        Checks is the status of the conversion is complete and, if so, converts to a Filelink

        *returns* [Filestack.Filelink]

        ```python
        filelink = av_convert.to_filelink()
        ```
        """
        if self.status != 'completed':
            raise Exception('Audio/video conversion not complete!')

        response = requests.get(self.url).json()
        handle = response['data']['url'].split('/')[-1]
        return filestack.models.Filelink(handle, apikey=self.apikey, security=self.security)

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
        return requests.get(self.url).json()['status']
