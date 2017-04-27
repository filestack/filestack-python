from filestack.version import __version__


class Filelink(object):

    FILESTACK_CDN_URL = 'https://cdn.filestackcontent.com/'
    HEADERS = {'User-Agent': 'filestack-python {}'.format(__version__)}

    def __init__(self, handle, apikey=None):
        self._apikey = apikey
        self._handle = handle

    @property
    def handle(self):
        return self._handle

    @property
    def url(self):
        return self.FILESTACK_CDN_URL + self._handle

    @property
    def apikey(self):
        return self._apikey

    @apikey.setter
    def apikey(self, apikey):
        self._apikey = apikey
