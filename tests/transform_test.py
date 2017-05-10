import pytest

from filestack import Client, Transform

APIKEY = 'SOMEAPIKEY'
HANDLE = 'SOMEHANDLE'
transform = Transform(HANDLE, apikey=APIKEY)

def test_sanity():
    assert transform.apikey == APIKEY
    assert transform.handle == HANDLE
    assert hasattr(transform, 'delete')
