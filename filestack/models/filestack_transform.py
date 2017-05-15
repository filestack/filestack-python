from filestack.config import ALLOWED_TRANFORMATION_METHODS
from filestack.exceptions import FilestackException
from filestack.mixins.filestack_imagetransform_mixin import ImageTransformationMixin
from filestack.mixins.filestack_common import CommonMixin


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

    def __get_attr__(self, attr_name):
        if attr_name not in ALLOWED_TRANFORMATION_METHODS:
            raise FilestackException('Method not allowed on Transform object')
        else:
            return getattr(self, attr_name)
