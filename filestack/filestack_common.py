import requests
import os
import mimetypes

from filestack.config import API_URL, FILE_PATH, HEADERS
from filestack.exceptions import SecurityError
from filestack.trafarets import CONTENT_DOWNLOAD_SCHEMA, OVERWRITE_SCHEMA, METADATA_SCHEMA

class CommonMixin(object):

    def download(self, destination_path, params=None, security=None):
        if params:
            CONTENT_DOWNLOAD_SCHEMA.check(params)
        with open(destination_path, 'wb') as f:
            response = self._make_call(API_URL, 'get',
                                       path=FILE_PATH,
                                       handle=self.handle,
                                       params=params,
                                       security_required=self.security)

            if response.ok:
                for chunk in response.iter_content(1024):
                    if not chunk:
                        break
                    f.write(chunk)
            return response

    def get_content(self, params=None, security=None):
        if params:
            CONTENT_DOWNLOAD_SCHEMA.check(params)
        response = self._make_call(API_URL, 'get',
                                   path=FILE_PATH,
                                   handle=self.handle,
                                   params=params,
                                   security_required=self.security)

        return response.content

    def delete(self, params=None):
        if params:
            params['key'] = self.apikey
        else:
            params = {'key': self.apikey}
        return self._make_call(API_URL, 'delete',
                               path=FILE_PATH,
                               handle=self.handle,
                               params=params,
                               security_required=True)

    def overwrite(self, url=None, filepath=None, params=None):
        if params:
            OVERWRITE_SCHEMA.check(params)
        data, files = None, None
        if url:
            data ={'url': url}
        elif filepath:
            filename = os.path.basename(filepath)
            mimetype = mimetypes.guess_type(filepath)[0]
            files = {'fileUpload': (filename, open(filepath, 'rb'), mimetype)}
        else:
            raise ValueError("You must include a url or filepath parameter")

        response = self._make_call(API_URL, 'post',
                                   path=FILE_PATH,
                                   params=params,
                                   data=data,
                                   files=files,
                                   security_required=True)

        new_file_info = response.json()
        return self.__class__(handle=new_file_info.get('handle'),
                              apikey=self.apikey,
                              security=self.security)

    def _make_call(self, base, action, handle=None, path=None, params=None, security_required=None, data=None, files=None):
        request_func = getattr(requests, action)
        if security_required is not None:
            if self.security is not None:
                url = self._get_url(base, path=path, handle=handle, security=self.security)
            else:
                raise SecurityError("Please provide either a signature/policy or a username/password")

        else:
            url = self._get_url(base, path=path, handle=handle)

        return request_func(url, params=params, headers=HEADERS, data=data, files=files)

    def _get_url(self, base, handle=None, path=None, security=None):
        url_components = [base]

        if path:
            url_components.append(path)

        if handle:
            url_components.append(handle)

        url_base = '/'.join(url_components)

        if security:
            return "{base}?policy={policy}&signature={signature}".format(
                base=url_base,
                policy=security['policy'],
                signature=security['signature'])

        return url_base
