from filestack.config import CDN_URL
from filestack.mixins import CommonMixin
from filestack.mixins import ImageTransformationMixin
from filestack.utils.utils import get_url, make_call, get_transform_url


class Filelink(ImageTransformationMixin, CommonMixin):
    """
    Filelinks are object representations of Filestack Filehandles. You can perform all actions that is allowed through our REST API,
    including downloading, deleting, overwriting and retrieving metadata. You can also get image tags, SFW filters, and directly
    call any of our available transformations.
    """

    def __init__(self, handle, apikey=None, security=None):
        self._apikey = apikey
        self._handle = handle
        self._security = security

    def tags(self):
        """
        Get Google Vision tags for the Filelink.

        *returns* [Dict]

        ```python
        from filestack import Client

        client = Client("<API_KEY>")
        filelink = client.upload(filepath='/path/to/file/foo.jpg')
        tags = filelink.tags()
        ```
        """
        return self._return_tag_task('tags')

    def sfw(self):
        """
        Get SFW label for the given file.

        *returns* [Boolean]

        ```python
        from filestack import Client

        client = Client("<API_KEY>")
        filelink = client.upload(filepath='/path/to/file/foo.jpg')
        # returns true if SFW and false if not
        sfw = filelink.sfw()
        ```
        """
        return self._return_tag_task('sfw')

    def _return_tag_task(self, task):
        """
        Runs both SFW and Tags tasks
        """
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
        """
        Returns the handle associated with the instance (if any)

        *returns* [String]

        ```python
        filelink.handle
        # YOUR_HANDLE
        ```
        """
        return self._handle

    @property
    def url(self):
        """
        Returns the URL for the instance, which can be used
        to retrieve, delete, and overwrite the file. If security is enabled, signature and policy parameters will
        be included,

        *returns* [String]

        ```python
        filelink = client.upload(filepath='/path/to/file')
        filelink.url
        # https://cdn.filestackcontent.com/FILE_HANDLE
        ```
        """
        return get_url(CDN_URL, handle=self.handle, security=self.security)

    @property
    def security(self):
        """
        Returns the security object associated with the instance (if any)

        *returns* [Dict]

        ```python
        filelink.security
        # {'policy': 'YOUR_ENCODED_POLICY', 'signature': 'YOUR_ENCODED_SIGNATURE'}
        ```
        """
        return self._security

    @property
    def apikey(self):
        """
        Returns the API key associated with the instance

        *returns* [String]

        ```python
        filelink.apikey
        # YOUR_API_KEY
        ```
        """
        return self._apikey

    @apikey.setter
    def apikey(self, apikey):
        self._apikey = apikey
