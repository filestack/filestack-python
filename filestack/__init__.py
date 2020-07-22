__version__ = '3.2.1'


class CFG:
    API_URL = 'https://www.filestackapi.com/api'
    DEFAULT_CHUNK_SIZE = 5 * 1024 ** 2
    DEFAULT_UPLOAD_MIMETYPE = 'application/octet-stream'

    HEADERS = {
        'User-Agent': 'filestack-python {}'.format(__version__),
        'Filestack-Source': 'Python-{}'.format(__version__)
    }

    def __init__(self):
        self.CNAME = ''

    @property
    def CDN_URL(self):
        return 'https://cdn.{}'.format(self.CNAME or 'filestackcontent.com')

    @property
    def MULTIPART_START_URL(self):
        return 'https://upload.{}/multipart/start'.format(
            self.CNAME or 'filestackapi.com'
        )


config = CFG()


from .models.client import Client
from .models.filelink import Filelink
from .models.security import Security
from .models.transformation import Transformation
from .models.audiovisual import AudioVisual
from .mixins.common import CommonMixin
from .mixins.imagetransformation import ImageTransformationMixin
