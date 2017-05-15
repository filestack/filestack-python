from filestack.config import API_URL, STORE_PATH, ALLOWED_CLIENT_METHODS
from filestack.exceptions import FilestackException
from filestack.mixins import CommonMixin, ImageTransformationMixin
from filestack.trafarets import STORE_LOCATION_SCHEMA, STORE_SCHEMA

import json
import filestack.models
import mimetypes
import os
import re


class Client(ImageTransformationMixin, CommonMixin):

    def __init__(self, apikey, security=None, storage='S3'):
        self._apikey = apikey
        self._security = security
        STORE_LOCATION_SCHEMA.check(storage)
        self._storage = storage

    def transform_external(self, external_url):
        return filestack.models.Transform(apikey=self.apikey, security=self.security, external_url=external_url)

    def upload(self, url=None, filepath=None, params=None):
        if params:
            STORE_SCHEMA.check(params)

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

        response = self._make_call(API_URL, 'post',
                                   path=path,
                                   params=params,
                                   data=data,
                                   files=files)

        if response.ok:
            data = json.loads(response.text)
            handle = re.match(r'(?:https:\/\/cdn\.filestackcontent\.com\/)(\w+)',
                              data['url']).group(1)
            return filestack.models.Filelink(handle, apikey=self.apikey, security=self.security)
        else:
            raise Exception(response.text)

    @property
    def security(self):
        return self._security

    @property
    def storage(self):
        return self._storage

    @property
    def apikey(self):
        return self._apikey

    def __getattr__(self, attr_name):
        if attr_name not in ALLOWED_CLIENT_METHODS:
            raise FilestackException('Method not allowed on Client object')
        else:
            return getattr(self, attr_name)
