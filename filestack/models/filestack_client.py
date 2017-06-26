import mimetypes
import os
import re

import filestack.models

from filestack.config import API_URL, CDN_URL, STORE_PATH
from filestack.trafarets import STORE_LOCATION_SCHEMA, STORE_SCHEMA
from filestack.utils import utils
from filestack.utils import upload_utils


class Client():

    def __init__(self, apikey, security=None, storage='S3'):
        self._apikey = apikey
        self._security = security
        STORE_LOCATION_SCHEMA.check(storage)
        self._storage = storage

    def transform_external(self, external_url):
        return filestack.models.Transform(apikey=self.apikey, security=self.security, external_url=external_url)

    def urlscreenshot(self, external_url, agent=None, mode=None, width=None, height=None, delay=None):
        params = locals()
        params.pop('self')
        params.pop('external_url')

        params = {k: v for k, v in params.items() if v is not None}

        url_task = utils.return_transform_task('urlscreenshot', params)

        new_transform = filestack.models.Transform(apikey=self.apikey, security=self.security, external_url=external_url)
        new_transform._transformation_tasks.append(url_task)

        return new_transform

    def zip(self, destination_path, files):

        zip_url = "{}/{}/zip/{}".format(CDN_URL, self.apikey, files)
        with open(destination_path, 'wb') as new_file:
            response = utils.make_call(zip_url, 'get')
            if response.ok:
                for chunk in response.iter_content(1024):
                    if not chunk:
                        break
                    new_file.write(chunk)

                return response

            return response.text

    def upload(self, url=None, filepath=None, multipart=True, params=None, upload_processes=None):
        if params:
            STORE_SCHEMA.check(params)

        if filepath and url:
            raise ValueError("Cannot upload file and external url at the same time")

        if multipart and filepath:
            response = upload_utils.multipart_upload(
                self.apikey, filepath, self.storage,
                upload_processes=upload_processes, params=params, security=self.security
            )
        else:
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

            if self.security:
                path = "{path}?policy={policy}&signature={signature}".format(
                    path=path, policy=self.security['policy'].decode('utf-8'),
                    signature=self.security['signature']
                )

            response = utils.make_call(
                API_URL, 'post', path=path, params=params, data=data, files=files
            )

        if response.ok:
            response = response.json()
            handle = re.match(
                r'(?:https:\/\/cdn\.filestackcontent\.com\/)(\w+)',
                response['url']
            ).group(1)
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
