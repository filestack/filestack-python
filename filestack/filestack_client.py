from filestack.config import API_URL, HEADERS, STORE_PATH, FILE_PATH
from filestack_common import CommonMixin
from .filestack_filelink import Filelink

import re
import json
import os
import mimetypes

class Client(CommonMixin):

    def __init__(self, apikey, security=None, storage='S3'):
        self._apikey = apikey
        self._security = security
        self._storage = storage

    def store(self, url=None, filepath=None, params=None):
        files, data = None, None
        if url:
            data = {'url': url}
        if filepath:
            filename = os.path.basename(filepath)
            mimetype = mimetypes.guess_type(filepath)[0]
            files = {'fileUpload': (filename, open(filepath, 'rb'), mimetype)}

        if params:
            params['key'] = self.apikey
        else:
            params = {'key': self.apikey}

        path = '{path}/{storage}'.format(path=STORE_PATH, storage=self.storage)

        response = self._make_call(API_URL, 'post', path=path, params=params, data=data, files=files)
        if response.ok:
            data = json.loads(response.text)
            handle = re.match(r'(?:https:\/\/)'
                              r'(?:www\.|cdn\.)'
                              r'(?:file\w+\.\w+\/)'
                              r'(\w+)',
                              data['url']).group(1)
            return Filelink(handle, apikey=self.apikey, security=self.security)

    @property
    def security(self):
        return self._security

    @property
    def storage(self):
        return self._storage

    @property
    def apikey(self):
        return self._apikey
