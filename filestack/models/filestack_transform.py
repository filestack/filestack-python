from filestack.config import CDN_URL
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
        return utils.get_transform_url(self._transformation_tasks,
                                       external_url=self.external_url,
                                       handle=self.handle,
                                       security=self.security,
                                       apikey=self.apikey)
