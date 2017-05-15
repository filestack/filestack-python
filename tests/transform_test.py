import pytest

from filestack import Client, Transform
from filestack.config import CDN_URL, API_URL

APIKEY = 'SOMEAPIKEY'
HANDLE = 'SOMEHANDLE'
EXTERNAL_URL = 'SOMEEXTERNALURL'


@pytest.fixture
def transform():
    return Transform(apikey=APIKEY, external_url=EXTERNAL_URL)

def test_sanity(transform):
    assert transform.apikey == APIKEY
    assert transform.external_url == EXTERNAL_URL
    assert hasattr(transform, 'delete')

def test_resize(transform):
    target_url = 'https://cdn.filestackcontent.com/{}/resize=width:500,height:500/{}'.format(APIKEY,
                                                                                            EXTERNAL_URL)
    resize = transform.resize(width=500, height=500)
    assert transform.get_transformation_url() == target_url

def test_crop(transform):
    target_url = 'https://cdn.filestackcontent.com/{}/crop=dim:500/{}'.format(APIKEY,
                                                                          EXTERNAL_URL)
    resize = transform.crop(dim=500)
    assert transform.get_transformation_url() == target_url

def test_rotate(transform):
    target_url = 'https://cdn.filestackcontent.com/{}/rotate=deg:90/{}'.format(APIKEY,
                                                                        EXTERNAL_URL)
    resize = transform.rotate(deg=90)
    assert transform.get_transformation_url() == target_url

def test_flip(transform):
    target_url = 'https://cdn.filestackcontent.com/{}/flip/{}'.format(APIKEY,
                                                                      EXTERNAL_URL)
    resize = transform.flip()
    assert transform.get_transformation_url() == target_url

