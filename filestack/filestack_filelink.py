from filestack.version import __version__


class Filelink(object):

    HEADERS = {'User-Agent': 'filestack-python {}'.format(__version__)}

    def __init__(self, apikey=None):
        self._apikey = apikey

    def get_apikey(self):
        return self._apikey

    def set_apikey(self, apikey):
        self._apikey = apikey

    apikey = property(get_apikey, set_apikey)
