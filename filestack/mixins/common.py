import filestack.models
from filestack.utils import requests


class CommonMixin:
    """
    Contains all functions related to the manipulation of Filelink and Transformation objects
    """

    @property
    def url(self):
        """
        Returns object's URL

        >>> filelink.url
        'https://cdn.filestackcontent.com/FILE_HANDLE'
        >>> transformation.url
        'https://cdn.filestackcontent.com/resize=width:800/FILE_HANDLE'

        Returns:
            str: object's URL
        """
        return self._build_url()

    def signed_url(self, security=None):
        """
        Returns object's URL signed using security object

        >>> filelink.url
        'https://cdn.filestackcontent.com/security=p:<encoded_policy>,s:<signature>/FILE_HANDLE'
        >>> transformation.url
        'https://cdn.filestackcontent.com/resize=width:800/security=p:<encoded_policy>,s:<signature>/FILE_HANDLE'

        Args:
            security (:class:`filestack.Security`): Security object that will be used
                to sign url

        Returns:
            str: object's signed URL
        """
        sec = security or self.security
        if sec is None:
            raise ValueError('Security is required to sign url')
        return self._build_url(security=sec)

    def store(self, filename=None, location=None, path=None, container=None,
              region=None, access=None, base64decode=None, workflows=None):
        """
        Stores current object as a new :class:`filestack.Filelink`.

        Args:
            filename (str): name for the stored file
            location (str): your storage location, one of: :data:`"s3"` :data:`"azure"`
                :data:`"dropbox"` :data:`"rackspace"` :data:`"gcs"`
            container (str): the bucket or container (folder) in which to store the file
                (does not apply when storing to Dropbox)
            path (str): the path to store the file within the specified container
            region (str): your storage region (applies to S3 only)
            access (str): :data:`"public"` or :data:`"private"` (applies to S3 only)
            base64decode (bool): indicates if content should be decoded before it is stored
            workflows (list): IDs of `Filestack Workflows
                <https://www.filestack.com/products/workflows>`_ that should be triggered after upload

        Returns:
            :class:`filestack.Filelink`: new Filelink object
        """
        if path:
            path = '"{}"'.format(path)
        instance = self._add_transform_task('store', locals())
        response = requests.post(instance.url)
        return filestack.models.Filelink(handle=response.json()['handle'])

    def download(self, path, security=None):
        """
        Downloads a file to the given local path and returns the size of the downloaded file if successful
        """
        sec = security or self.security
        total_bytes = 0

        with open(path, 'wb') as f:
            response = requests.get(self._build_url(security=sec), stream=True)
            for data_chunk in response.iter_content(5 * 1024 ** 2):
                f.write(data_chunk)
                total_bytes += len(data_chunk)

        return total_bytes

    def get_content(self, security=None):
        """
        Returns the raw byte content of a given object

        Returns:
            `bytes`: file content
        """
        sec = security or self.security
        response = requests.get(self._build_url(security=sec))
        return response.content

    def tags(self, security=None):
        """
        Performs image tagging operation on current object

        Args:
            security (:class:`filestack.Security`): Security object that will be used
                to perform image tagging

        Returns:
            `dict`: dictionary containing image tags
        """
        obj = self._add_transform_task('tags', params={'self': None})
        response = requests.get(obj.signed_url(security=security))
        return response.json()

    def sfw(self, security=None):
        """
        Performs Safe for Work detection on current object (image).

        Args:
            security (:class:`filestack.Security`): Security object that will be used
                to perform image tagging

        Returns:
            `dict`: dictionary containing SFW result
        """
        obj = self._add_transform_task('sfw', params={'self': None})
        response = requests.get(obj.signed_url(security=security))
        return response.json()
