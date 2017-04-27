from filestack.version import __version__


class Client(object):

    API_URL = 'https://www.filestackapi.com/api'
    HEADERS = {'User-Agent': 'filestack-python {}'.format(__version__)}

    def __init__(self, apikey):
        self._apikey = apikey

    @property
    def apikey(self):
        return self._apikey
