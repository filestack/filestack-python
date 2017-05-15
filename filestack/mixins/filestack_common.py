import filestack.models
import mimetypes
import os
import requests

from filestack.config import CDN_URL, API_URL, FILE_PATH, HEADERS
from filestack.trafarets import CONTENT_DOWNLOAD_SCHEMA, OVERWRITE_SCHEMA


class CommonMixin(object):

    def download(self, destination_path, params=None):
        if params:
            CONTENT_DOWNLOAD_SCHEMA.check(params)
        with open(destination_path, 'wb') as f:
            response = self._make_call(CDN_URL, 'get',
                                       handle=self.handle,
                                       params=params)

            if response.ok:
                for chunk in response.iter_content(1024):
                    if not chunk:
                        break
                    f.write(chunk)
            return response

    def get_content(self, params=None):
        if params:
            CONTENT_DOWNLOAD_SCHEMA.check(params)
        response = self._make_call(CDN_URL, 'get',
                                   handle=self.handle,
                                   params=params)

        return response.content

    def delete(self, params=None):
        if params:
            params['key'] = self.apikey
        else:
            params = {'key': self.apikey}
        return self._make_call(API_URL, 'delete',
                               path=FILE_PATH,
                               handle=self.handle,
                               params=params)

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

        return self._make_call(API_URL, 'post',
                               path=FILE_PATH,
                               params=params,
                               handle=self.handle,
                               data=data,
                               files=files)

    def get_url(self):
        if self.security is not None:
            url = self._get_url(CDN_URL, handle=self.handle, security=self.security)
        else:
            url = self._get_url(CDN_URL, handle=self.handle)

        return url

    def _make_call(self, base, action, handle=None, path=None, params=None, data=None, files=None):
        request_func = getattr(requests, action)

        if isinstance(self, filestack.models.Transform):
            return request_func(self.get_transformation_url(), params=params, headers=HEADERS, data=data, files=files)

        if self.security is not None:
            url = self._get_url(base, path=path, handle=handle, security=self.security)
        else:
            url = self._get_url(base, path=path, handle=handle)

        return request_func(url, params=params, headers=HEADERS, data=data, files=files)

    def _get_url(self, base, handle=None, path=None, security=None):
        url_components = [base]

        if path:
            url_components.append(path)

        if security:
            url_components.append('security=policy:{policy},signature:{signature}'.format(policy=self.security['policy'],
                                                                                          signature=self.security['signature']))
        if handle:
            url_components.append(handle)

        return '/'.join(url_components)
