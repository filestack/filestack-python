from filestack import config
from filestack.mixins import CommonMixin
from filestack.mixins import ImageTransformationMixin


class Filelink(ImageTransformationMixin, CommonMixin):
    """
    Filelinks are object representations of Filestack Filehandles.
    You can perform all actions that is allowed through our REST API,
    including downloading, deleting, overwriting and retrieving metadata.
    You can also get image tags, SFW filters, and directly
    call any of our available transformations.
    """

    def __init__(self, handle, apikey=None, security=None):
        self._apikey = apikey
        self._handle = handle
        self.security = security

    def __repr__(self):
        return '<Filelink {}>'.format(self.handle)

    @property
    def handle(self):
        return self._handle

    # TODO - add tags & stw for filelink
    # TODO - add delete() method

    @property
    def url(self):
        """
        Returns filelink's URL

        *returns* [String]

        ```python
        filelink = client.upload(filepath='/path/to/file')
        filelink.url
        # https://cdn.filestackcontent.com/FILE_HANDLE
        ```
        """
        return self._build_url()

    def signed_url(self, security=None):
        sec = security or self.security  # TODO test overwriting default security
        if sec is None:
            raise Exception('Ssecurity object is required to sign url')
        return self._build_url(security=sec)

    def _build_url(self, security=None):
        url_elements = [config.CDN_URL, self.handle]
        if security is not None:
            url_elements.insert(-1, security.as_url_string())
        return '/'.join(url_elements)
