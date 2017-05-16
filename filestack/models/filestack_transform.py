from filestack.config import CDN_URL
from filestack.mixins import ImageTransformationMixin, CommonMixin

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
        url_components = [CDN_URL]
        if self.external_url:
            url_components.append(self.apikey)
        if self.security:
            url_components.append('security=policy:{},signature:{}'.format(self.security['policy'],
                                                                           self.security['signature']))
        url_components.append('/'.join(self._transformation_tasks))
        url_components.append(self.handle or self.external_url)

        return '/'.join(url_components)
