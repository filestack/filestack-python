import io
import os
import sys
import mimetypes
import multiprocessing
import hashlib
import logging
import functools
import threading
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor

from base64 import b64encode

from filestack.utils import requests

from filestack import config

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s - %(processName)s[%(process)d] - %(levelname)s - %(message)s"))
log.addHandler(handler)

MB = 1024 ** 2
DEFAULT_PART_SIZE = 8 * MB
CHUNK_SIZE = 8 * MB
MIN_CHUNK_SIZE = 32 * 1024
MAX_DELAY = 4
NUM_THREADS = multiprocessing.cpu_count()

lock = threading.Lock()


def decrease_chunk_size():
    global CHUNK_SIZE
    CHUNK_SIZE //= 2
    if CHUNK_SIZE < MIN_CHUNK_SIZE:
        raise Exception('Minimal chunk size failed')


def upload_part(apikey, filename, filepath, filesize, storage, start_response, part):
    with open(filepath, 'rb') as f:
        f.seek(part['seek_point'])
        part_bytes = io.BytesIO(f.read(DEFAULT_PART_SIZE))

    payload_base = {
        'apikey': apikey,
        'uri': start_response['uri'],
        'region': start_response['region'],
        'upload_id': start_response['upload_id'],
        'store': {'location': storage},
        'part': part['num']
    }

    global CHUNK_SIZE
    chunk_data = part_bytes.read(CHUNK_SIZE)
    offset = 0

    while chunk_data:
        payload = payload_base.copy()
        payload.update({
            'size': len(chunk_data),
            'md5': b64encode(hashlib.md5(chunk_data).digest()).strip().decode('utf-8'),
            'offset': offset,
            'fii': True
        })

        try:
            url = 'https://{}/multipart/upload'.format(start_response['location_url'])
            api_resp = requests.post(url, json=payload).json()
            s3_resp = requests.put(api_resp['url'], headers=api_resp['headers'], data=chunk_data)
            if not s3_resp.ok:
                raise Exception('Incorrect S3 response')
            offset += len(chunk_data)
            chunk_data = part_bytes.read(CHUNK_SIZE)
        except Exception as e:
            log.error('Upload failed: %s', str(e))
            with lock:
                if CHUNK_SIZE >= len(chunk_data):
                    decrease_chunk_size()

            part_bytes.seek(offset)
            chunk_data = part_bytes.read(CHUNK_SIZE)

    payload = payload_base.copy()
    payload.update({'size': filesize})

    url = 'https://{}/multipart/commit'.format(start_response['location_url'])
    requests.post(url, json=payload)


def upload(apikey, filepath, file_obj, storage, params=None, security=None):
    params = params or {}

    filename = params.get('filename') or os.path.split(filepath)[1]
    mimetype = params.get('mimetype') or mimetypes.guess_type(filepath)[0] or config.DEFAULT_UPLOAD_MIMETYPE
    filesize = os.path.getsize(filepath)

    payload = {
        'apikey': apikey,
        'filename': filename,
        'mimetype': mimetype,
        'size': filesize,
        'fii': True,
        'store': {
            'location': storage
        }
    }

    for key in ('path', 'location', 'region', 'container', 'access'):
        if key in params:
            payload['store'][key] = params[key]

    if security:
        payload.update({
            'policy': security.policy_b64,
            'signature': security.signature
        })

    start_response = requests.post(config.MULTIPART_START_URL, json=payload).json()
    parts = [
        {
            'seek_point': seek_point,
            'num': num + 1
        } for num, seek_point in enumerate(range(0, filesize, DEFAULT_PART_SIZE))
    ]

    fii_upload = functools.partial(
        upload_part, apikey, filename, filepath, filesize, storage, start_response
    )

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        list(executor.map(fii_upload, parts))

    payload.update({
        'uri': start_response['uri'],
        'region': start_response['region'],
        'upload_id': start_response['upload_id'],
    })

    if 'workflows' in params:
        payload['store']['workflows'] = params.pop('workflows')

    if 'upload_tags' in params:
        payload['upload_tags'] = params.pop('upload_tags')

    complete_url = 'https://{}/multipart/complete'.format(start_response['location_url'])
    session = requests.Session()
    retries = Retry(total=7, backoff_factor=0.2, status_forcelist=[202], allowed_methods=frozenset(['POST']))
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))
    response = session.post(complete_url, json=payload, headers=config.HEADERS)
    if response.status_code != 200:
        log.error('Did not receive a correct complete response: %s. Content %s', response, response.content)
        raise Exception('Invalid complete response: {}'.format(response.content))

    return response.json()
