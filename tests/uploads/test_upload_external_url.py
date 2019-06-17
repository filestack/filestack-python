from unittest.mock import patch

import pytest

from tests.helpers import DummyHttpResponse
from filestack import config
from filestack.uploads.external_url import upload_external_url

url = 'http://image.url'
apikey = 'TESTAPIKEY'


@patch('filestack.uploads.external_url.requests.post')
def test_upload_without_store_params(post_mock):
    post_mock.return_value = DummyHttpResponse(json_dict={'handle': 'newHandle'})

    handle = upload_external_url(url, apikey)
    assert handle == 'newHandle'
    post_mock.assert_called_once_with('{}/{}/store/{}'.format(config.CDN_URL, apikey, url))


@patch('filestack.uploads.external_url.requests.post')
def test_upload_exception(post_mock):
    error_message = 'Oops!'
    post_mock.side_effect = Exception(error_message)

    with pytest.raises(Exception, match=error_message):
        upload_external_url(url, apikey)
