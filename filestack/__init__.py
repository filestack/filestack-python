__version__ = '3.5.0'


class CFG:
    API_URL = 'https://www.filestackapi.com/api'

    CDN_DOMAIN = 'filestackcontent.com'
    UPLOAD_DOMAIN = 'filestackapi.com'

    CDN_SUBDOMAIN = 'cdn'
    UPLOAD_SUBDOMAIN = 'upload'

    REQUEST_PROTOCOL = 'https://'
    MULTIPART_START_PATH = '/multipart/start'
    MULTIPART_UPLOAD_PATH = '/multipart/upload'
    MULTIPART_COMMIT_PATH = '/multipart/commit'
    MULTIPART_COMPLETE_PATH = '/multipart/complete'

    DEFAULT_CHUNK_SIZE = 5 * 1024 ** 2
    DEFAULT_UPLOAD_MIMETYPE = 'application/octet-stream'

    HEADERS = {
        'User-Agent': 'filestack-python {}'.format(__version__),
        'Filestack-Source': 'Python-{}'.format(__version__)
    }

    def __init__(self):
        self._cname = ''

    @property
    def _upload_url(self):
        return "{}{}.{}".format(
            self.REQUEST_PROTOCOL,
            self.UPLOAD_SUBDOMAIN,
            self.UPLOAD_DOMAIN,
        )

    @property
    def CNAME(self):
        return self._cname

    @CNAME.setter
    def CNAME(self, new_cname):
        if not isinstance(new_cname, str):
            raise ValueError("CNAME needs to be set as a non empty string")
        if new_cname == "":
            raise ValueError("CNAME should not be empty")

        self._cname = new_cname
        self.CDN_DOMAIN = new_cname
        self.UPLOAD_DOMAIN = new_cname

    @property
    def CDN_URL(self):
        return "{}{}.{}".format(
            self.REQUEST_PROTOCOL,
            self.CDN_SUBDOMAIN,
            self.CDN_DOMAIN,
        )

    @property
    def MULTIPART_START_URL(self):
        return self._upload_url + self.MULTIPART_START_PATH


config = CFG()


from .models.client import Client
from .models.filelink import Filelink
from .models.security import Security
from .models.transformation import Transformation
from .models.audiovisual import AudioVisual
from .mixins.common import CommonMixin
from .mixins.imagetransformation import ImageTransformationMixin
