from filestack.config import FILESTACK_CDN_URL
from filestack.version import __version__
from filestack.filestack_common import CommonMixin

class Filelink(CommonMixin):

    def __init__(self, handle, apikey=None, security=None):
        self._apikey = apikey
        self._handle = handle
        self.FILESTACK_CDN_URL = FILESTACK_CDN_URL
        self._security = security

    @property
    def handle(self):
        return self._handle

    @property
    def url(self):
        return self.FILESTACK_CDN_URL + self._handle

    @property
    def security(self):
        return self._security

    @property
    def apikey(self):
        return self._apikey

    @apikey.setter
    def apikey(self, apikey):
        self._apikey = apikey
