from filestack import config

from filestack.mixins import ImageTransformationMixin, CommonMixin


class Transformation(ImageTransformationMixin, CommonMixin):
    """
    Transformation objects take either a handle or an external URL. They act similarly to
    Filelinks, but have specific methods like store, debug, and also construct
    URLs differently.

    Transformation objects can be chained to build up multi-task transform URLs, each one saved in
    self._transformation_tasks
    """

    def __init__(self, apikey=None, handle=None, external_url=None, security=None):
        self.apikey = apikey
        self.handle = handle
        self.security = security
        self.external_url = external_url
        self._transformation_tasks = []

    def _build_url(self, security=None):
        url_elements = [config.CDN_URL, self.handle or self.external_url]

        if self._transformation_tasks:
            tasks_str = '/'.join(self._transformation_tasks)
            url_elements.insert(1, tasks_str)

        if self.external_url:
            url_elements.insert(1, self.apikey)

        if security is not None:
            url_elements.insert(-1, security.as_url_string())
        return '/'.join(url_elements)
