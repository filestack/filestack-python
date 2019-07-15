from filestack import config

from filestack.mixins import ImageTransformationMixin, CommonMixin


class Transformation(ImageTransformationMixin, CommonMixin):
    """
    Transformation objects represent the result of image transformation performed
    on Filelinks or other Transformations (as they can be chained).
    Unless explicitly stored, no Filelinks are created when
    image transformations are performed.

    >>> from filestack import Filelink
    >>> transformation= Filelink('sm9IEXAMPLEQuzfJykmA').resize(width=800)
    >>> transformation.url
    'https://cdn.filestackcontent.com/resize=width:800/sm9IEXAMPLEQuzfJykmA'
    >>> new_filelink = transformation.store()
    >>> new_filelink.url
    'https://cdn.filestackcontent.com/NEW_HANDLE'
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
