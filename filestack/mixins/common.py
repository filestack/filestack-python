import filestack.models
from filestack.utils import requests


class CommonMixin(object):
    """
    Contains all functions related to the manipulation of Filelinks
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
        sec = security or self.security
        if sec is None:
            raise ValueError('Security is required to sign url')
        return self._build_url(security=sec)

    def store(self, filename=None, location=None, path=None, container=None,
              region=None, access=None, base64decode=None, workflows=None):
        instance = self.add_transform_task('store', locals())
        response = requests.post(instance.url)
        return filestack.models.Filelink(handle=response.json()['handle'])

    def download(self, destination_path, security=None):
        """
        Downloads a file to the given local path and returns the size of the downloaded file if successful
        """
        sec = security or self.security
        total_bytes = 0

        with open(destination_path, 'wb') as f:
            response = requests.get(self._build_url(security=sec), stream=True)
            for data_chunk in response.iter_content(5 * 1024 ** 2):
                f.write(data_chunk)
                total_bytes += len(data_chunk)

        return total_bytes

    def get_content(self, security=None):
        """
        Returns the raw byte content of a given object
        """
        sec = security or self.security
        response = requests.get(self._build_url(security=sec))
        return response.content

    def tags(self, security=None):
        obj = self.add_transform_task('tags', params={'self': None})
        response = requests.get(obj.signed_url(security=security))
        return response.json()

    def sfw(self, security=None):
        obj = self.add_transform_task('sfw', params={'self': None})
        response = requests.get(obj.signed_url(security=security))
        return response.json()
