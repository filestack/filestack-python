from filestack.config import FILESTACK_CDN_URL

class Filelink(object):

    def __init__(self, handle, apikey=None):
        self._apikey = apikey
        self._handle = handle
        self.FILESTACK_CDN_URL = FILESTACK_CDN_URL

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
