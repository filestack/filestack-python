from filestack.config import CDN_URL
from filestack.mixins import CommonMixin
from filestack.mixins import ImageTransformationMixin
from filestack.utils.utils import get_url, make_call, get_transform_url
from filestack.version import __version__


class Filelink(ImageTransformationMixin, CommonMixin):

    def __init__(self, handle, apikey=None, security=None):
        self._apikey = apikey
        self._handle = handle
        self._security = security

    def tags(self):
        return self._return_tag_task('tags')

    def sfw(self):
        return self._return_tag_task('sfw')

    def _return_tag_task(self, task):
        if self.security is None:
            raise Exception('Tags require security')
        tasks = [task]
        transform_url = get_transform_url(
            tasks, handle=self.handle, security=self.security,
            apikey=self.apikey
        )
        response = make_call(
            CDN_URL, 'get', handle=self.handle, security=self.security,
            transform_url=transform_url
        )
        return response.json()

    @property
    def handle(self):
        return self._handle

    @property
    def url(self):
        return get_url(CDN_URL, handle=self.handle, security=self.security)

    @property
    def security(self):
        return self._security

    @property
    def apikey(self):
        return self._apikey

    @apikey.setter
    def apikey(self, apikey):
        self._apikey = apikey
