import requests
import os
import mimetypes

from filestack.config import API_URL, FILE_PATH, HEADERS

class CommonMixin(object):

    def download(self, destination_path, params=None, security=None):
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
        response = self._make_call(API_URL, 'get',
                                    path=FILE_PATH,
                                    handle=self.handle,
                                    params=params,
                                    security_required=self.security)

        return response.content

    def delete(self, params=None):
        return self._make_call(API_URL, 'delete', path=FILE_PATH, params=params, security_required=True)

    def overwrite(self, url=None, filepath=None, params=None):
        data = {}
        if url:
            data['url'] = url
        elif filepath:
            filename = os.path.basename(filepath)
            mimetype = mimetypes.guess_type(filepath)[0]
            files = {'fileUpload': (filename, open(filepath, 'rb'), mimetype)}
        else:
            return "You must specify a filepath or URL"

        return self._make_call(API_URL, 'post', path=FILE_PATH, params=params, data=data, files=files, security_required=True)

    def _make_call(self, base, action, handle=None, path=None, params=None, security_required=False, data=None, files=None):
        request_func = getattr(requests, action)

        if security_required is not None:

            if self.security is not None:
                url = self._get_url(base, path=path, handle=handle, security=self.security)

            else:
                return "Please provide either a signature/policy or a username/password"

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
