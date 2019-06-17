import io
import os
import sys
import mimetypes
import hashlib
import logging
import time
import functools
from multiprocessing.pool import ThreadPool
import threading

from base64 import b64encode

import requests

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
NUM_THREADS = 4

lock = threading.Lock()


def filestack_request(request_url, payload):
    response = requests.post(request_url, json=payload, headers=config.HEADERS)

    if not response.ok:
        raise Exception(response.text)

    return response


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
            api_resp = filestack_request(url, payload).json()
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
    filestack_request(url, payload)


def upload(apikey, filepath, storage, params=None, security=None):
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
            'policy': security['policy'].decode('utf-8'),
            'signature': security['signature']
        })

    start_response = filestack_request(config.MULTIPART_START_URL, payload).json()
    parts = [
        {
            'seek_point': seek_point,
            'num': num + 1
        } for num, seek_point in enumerate(range(0, filesize, DEFAULT_PART_SIZE))
    ]

    fii_upload = functools.partial(
        upload_part, apikey, filename, filepath, filesize, storage, start_response
    )

    pool = ThreadPool(NUM_THREADS)
    pool.map(fii_upload, parts)
    pool.close()

    payload.update({
        'uri': start_response['uri'],
        'region': start_response['region'],
        'upload_id': start_response['upload_id'],
    })

    if params.get('workflows'):
        payload['store']['workflows'] = params['workflows']

    complete_url = 'https://{}/multipart/complete'.format(start_response['location_url'])
    for wait_time in (0, 1, 2, 3, 5):
        time.sleep(wait_time)
        complete_response = requests.post(complete_url, json=payload, headers=config.HEADERS)
        log.debug('Complete response: %s. Content: %s', complete_response, complete_response.content)
        if complete_response.status_code == 200:
            break
    else:
        log.error('Did not receive a correct complete response: %s. Content %s', complete_response, complete_response.content)
        raise

    return complete_response
