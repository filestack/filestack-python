from filestack.config import CDN_URL
from filestack.mixins import CommonMixin
from filestack.mixins import ImageTransformationMixin
from filestack.version import __version__


class Filelink(ImageTransformationMixin, CommonMixin):

    def __init__(self, handle, apikey=None, security=None):
        # super(Filelink, self).__init__()
        self._apikey = apikey
        self._handle = handle
        self._security = security

    @property
    def handle(self):
        return self._handle

    @property
    def url(self):
        return "{}/{}".format(CDN_URL, self._handle)

    @property
    def security(self):
        return self._security

    @property
    def apikey(self):
        return self._apikey

    @apikey.setter
    def apikey(self, apikey):
        self._apikey = apikey
