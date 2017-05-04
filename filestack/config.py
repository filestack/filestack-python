from filestack.version import __version__

ACCEPTED_SECURITY_TYPES = {'expiry': int, 'call': list,
                           'handle': str, 'url': str,
                           'maxSize': int, 'minSize': int,
                           'path': str, 'container': str}

API_URL = 'https://www.filestackapi.com/api'
FILESTACK_CDN_URL = 'https://cdn.filestackcontent.com/'
HEADERS = {'User-Agent': 'filestack-python {}'.format(__version__)}
STORE_PATH = 'store'
FILE_PATH = 'file'
