class Client(object):

    def __init__(self, apikey):
        self._apikey = apikey

    @property
    def apikey(self):
        return self._apikey
