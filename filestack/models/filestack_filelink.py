from filestack import config
from filestack.utils import requests
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
        self.apikey = apikey
        self.handle = handle
        self.security = security

    def __repr__(self):
        return '<Filelink {}>'.format(self.handle)

    def _build_url(self, security=None):
        url_elements = [config.CDN_URL, self.handle]
        if security is not None:
            url_elements.insert(-1, security.as_url_string())
        return '/'.join(url_elements)

    def metadata(self, attributes_list, security=None):
        attr_string = '[{}]'.format(','.join(attributes_list))
        obj = self.add_transform_task('metadata', params={'self': None, 'p': attr_string})
        return requests.get(obj._build_url(security=security or self.security)).json()

    def delete(self, apikey=None, security=None):
        sec = security or self.security
        apikey = apikey or self.apikey

        if sec is None:
            raise Exception('Security object is required to delete filelink')

        if apikey is None:
            raise Exception('Apikey is required to delete filelink')

        url = '{}/file/{}'.format(config.API_URL, self.handle)
        delete_params = {
            'key': apikey,
            'policy': sec.policy_b64,
            'signature': sec.signature
        }
        requests.delete(url, params=delete_params)
