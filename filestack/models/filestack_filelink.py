import requests

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

    # TODO - add delete() method

    def _build_url(self, security=None):
        url_elements = [config.CDN_URL, self.handle]
        if security is not None:
            url_elements.insert(-1, security.as_url_string())
        return '/'.join(url_elements)

    def get_metadata(self, params=None, security=None):
        """
        Metadata provides certain information about a Filehandle, and you can specify
        which pieces of information you will receive back by passing in optional parameters.

        ```python
        from filestack import Client

        client =  Client('API_KEY')
        filelink = client.upload(filepath='/path/to/file/foo.jpg')
        metadata = filelink.get_metadata()
        # or define specific metadata to receive
        metadata = filelink.get_metadata({'filename': true})
        ```
        """
        # TODO should we allow only specific params here?
        params = params or {}
        sec = security or self.security
        request_url = self.url + '/metadata'

        if sec is not None:
            params.update({'policy': sec.policy_b64, 'signature': sec.signature})

        response = requests.get(request_url, params=params)
        if not response.ok:
            raise Exception(response.text)

        return response.json()
