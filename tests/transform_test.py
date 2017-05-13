import pytest

from filestack import Client, Transform

APIKEY = 'SOMEAPIKEY'
HANDLE = 'SOMEHANDLE'

@pytest.fixture
def transform():
    return Transform(HANDLE, apikey=APIKEY)

def test_sanity(transform):
    assert transform.apikey == APIKEY
    assert transform.handle == HANDLE
    assert hasattr(transform, 'delete')
