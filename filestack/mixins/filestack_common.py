import mimetypes
import os

import filestack.models

from filestack.config import CDN_URL, API_URL, FILE_PATH, METADATA_PATH
from filestack.trafarets import CONTENT_DOWNLOAD_SCHEMA, OVERWRITE_SCHEMA
from filestack.utils import utils


class CommonMixin(object):

    def download(self, destination_path, params=None):
        if params:
            CONTENT_DOWNLOAD_SCHEMA.check(params)
        with open(destination_path, 'wb') as new_file:
            response = utils.make_call(CDN_URL, 'get',
                                       handle=self.handle,
                                       params=params,
                                       security=self.security,
                                       transform_url=(self.url if isinstance(self, filestack.models.Transform) else None))

            if response.ok:
                for chunk in response.iter_content(1024):
                    if not chunk:
                        break
                    new_file.write(chunk)

            return response


    def get_content(self, params=None):
        if params:
            CONTENT_DOWNLOAD_SCHEMA.check(params)
        response = utils.make_call(CDN_URL, 'get',
                                   handle=self.handle,
                                   params=params,
                                   security=self.security,
                                   transform_url=(self.url if isinstance(self, filestack.models.Transform) else None))

        return response.content


    def get_metadata(self, params=None):
        metadata_url = "{CDN_URL}/{handle}/metadata".format(
            CDN_URL=CDN_URL, handle=self.handle
        )
        response = utils.make_call(metadata_url, 'get',
                                   params=params,
                                   security=self.security)
        return response.json()


    def delete(self, params=None):
        if params:
            params['key'] = self.apikey
        else:
            params = {'key': self.apikey}
        return utils.make_call(API_URL, 'delete',
                               path=FILE_PATH,
                               handle=self.handle,
                               params=params,
                               security=self.security,
                               transform_url=self.url if isinstance(self, filestack.models.Transform) else None)


    def overwrite(self, url=None, filepath=None, params=None):
        if params:
            OVERWRITE_SCHEMA.check(params)
        data, files = None, None
        if url:
            data = {'url': url}
        elif filepath:
            filename = os.path.basename(filepath)
            mimetype = mimetypes.guess_type(filepath)[0]
            files = {'fileUpload': (filename, open(filepath, 'rb'), mimetype)}
        else:
            raise ValueError("You must include a url or filepath parameter")

        return utils.make_call(API_URL, 'post',
                               path=FILE_PATH,
                               params=params,
                               handle=self.handle,
                               data=data,
                               files=files,
                               security=self.security,
                               transform_url=self.url if isinstance(self, filestack.models.Transform) else None)
