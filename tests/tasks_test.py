import re

import pytest
import responses

from filestack import Transformation, AudioVisual
from filestack import config

APIKEY = 'SOMEAPIKEY'
HANDLE = 'SOMEHANDLE'
EXTERNAL_URL = 'SOMEEXTERNALURL'


@pytest.fixture
def transform():
    return Transformation(apikey=APIKEY, external_url=EXTERNAL_URL)


def test_createpdf(transform):
    target_url = '{}/{}/pdfcreate/{}/[v7MSSKswR0mvEwZS9LD0,Sr5CrtQPSs5TTZzor1Cw]'.format(config.CDN_URL, APIKEY, EXTERNAL_URL)
    obj = transform.pdfcreate(engine='mupdf')
    assert obj.url

def test_animate(transform):
    target_url = '{}/{}/animate=fit:scale,width:200,height:300/{}/[OjKeBAuBTIWygi1NE8fx,WTY6jjIaTPOvWY9KsNh9]'.format(config.CDN_URL, APIKEY, EXTERNAL_URL)
    obj = transform.animate(fit='scale',width=200,height=300,loop=0,delay=1000)
    assert obj.url

def test_doc_to_images(transform):
    target_url = '{}/{}/doc_to_images/{}/3zOWSOLQ0SEdphqVil9Q'.format(config.CDN_URL, APIKEY, EXTERNAL_URL)
    obj = transform.doc_to_images(pages=[1], engine='imagemagick', format='png', quality=100, density=100, hidden_slides=False)
    assert obj.url

def test_smart_crop(transform):
    target_url = '{}/{}/smart_crop=width:100,height:100/{}/v7MSSKswR0mvEwZS9LD0'.format(config.CDN_URL, APIKEY, EXTERNAL_URL)
    obj = transform.smart_crop(width=100, height=100)
    assert obj.url

def test_pdf_convert(transform):
    target_url = '{}/{}/pdfconvert=pageorientation:landscape/{}/3zOWSOLQ0SEdphqVil9Q'.format(config.CDN_URL, APIKEY, EXTERNAL_URL)
    obj = transform.pdf_convert(pageorientation='landscape', pageformat='a4', metadata=True)
    assert obj.url

def test_fallback(transform):
    target_url = '{}/{}/{}'.format(config.CDN_URL, APIKEY, EXTERNAL_URL)
    obj = transform.fallback(file='3zOWSOLQ0SEdphqVil9Q', cache=12)
    assert obj.url
