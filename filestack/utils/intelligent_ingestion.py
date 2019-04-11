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
from filestack.utils.utils import store_params

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s - %(processName)s[%(process)d] - %(levelname)s - %(message)s"))
log.addHandler(handler)

MB = 1024 ** 2
DEFAULT_PART_SIZE = 8 * MB
CHUNK_SIZE = 8 * MB
MAX_DELAY = 4
NUM_THREADS = 4

lock = threading.Lock()


def filestack_request(request_url, request_data, filename):
    response = requests.post(
        request_url,
        data=request_data,
        files={'file': (filename, '', None)},
        headers=config.HEADERS
    )

    if not response.ok:
        raise Exception('Invalid Filestack API response')

    return response


def upload_part(apikey, filename, filepath, filesize, storage, start_response, part):
    log.debug('[%s] Working on part: %s', threading.get_ident(), part)
    with open(filepath, 'rb') as f:
        f.seek(part['seek_point'])
        part_bytes = io.BytesIO(f.read(DEFAULT_PART_SIZE))

    request_data_base = {
        'apikey': apikey,
        'uri': start_response['uri'],
        'region': start_response['region'],
        'upload_id': start_response['upload_id'],
        'store_location': storage,
        'part': part['num']
    }

    global CHUNK_SIZE
    chunk_data = part_bytes.read(CHUNK_SIZE)
    offset = 0

    while chunk_data:
        request_data = request_data_base.copy()
        request_data.update({
            'size': len(chunk_data),
            'md5': b64encode(hashlib.md5(chunk_data).digest()).strip(),
            'offset': offset,
            'multipart': True
        })
        try:
            api_resp = filestack_request(
                'https://{}/multipart/upload'.format(start_response['location_url']),
                request_data,
                filename
            )

            api_resp = api_resp.json()
            s3_resp = requests.put(api_resp['url'], headers=api_resp['headers'], data=chunk_data)
            if not s3_resp.ok:
                raise
            offset += len(chunk_data)
            chunk_data = part_bytes.read(CHUNK_SIZE)
        except Exception as e:
            log.error('Upload failed: %s', str(e))
            with lock:
                if CHUNK_SIZE >= len(chunk_data):
                    CHUNK_SIZE //= 2

            part_bytes.seek(offset)
            chunk_data = part_bytes.read(CHUNK_SIZE)

    request_data = request_data_base.copy()
    request_data.update({
        'size': filesize
    })

    filestack_request(
        'https://{}/multipart/commit'.format(start_response['location_url']),
        request_data,
        filename
    )


def upload(apikey, filepath, storage, params=None, security=None):
    params = params or {}

    filename = params.get('filename') or os.path.split(filepath)[1]
    mimetype = params.get('mimetype') or mimetypes.guess_type(filepath)[0] or config.DEFAULT_UPLOAD_MIMETYPE
    filesize = os.path.getsize(filepath)

    request_data = {
        'apikey': apikey,
        'filename': filename,
        'mimetype': mimetype,
        'size': filesize,
        'store_location': storage,
        'multipart': True
    }

    request_data.update(store_params(params))
    if security:
        request_data.update({
            'policy': security['policy'],
            'signature': security['signature']
        })

    start_response = filestack_request(config.MULTIPART_START_URL, request_data, filename).json()
    parts = [
        {
            'seek_point': seek_point,
            'num': num + 1
        } for num, seek_point in enumerate(range(0, filesize, DEFAULT_PART_SIZE))
    ]

    fii_upload = functools.partial(
        upload_part, apikey, filename, filepath, filesize, storage, start_response
    )

    with ThreadPool(4) as pool:
        pool.map(fii_upload, parts)

    request_data.update({
        'uri': start_response['uri'],
        'region': start_response['region'],
        'upload_id': start_response['upload_id'],
    })

    for wait_time in (0, 1, 2, 3, 5):
        time.sleep(wait_time)
        complete_response = requests.post(
            'https://{}/multipart/complete'.format(start_response['location_url']),
            data=request_data,
            files={'file': (filename, '', None)},
            headers=config.HEADERS
        )
        log.debug('Complete response: %s. Content: %s', complete_response, complete_response.content)
        if complete_response.status_code == 200:
            break
    else:
        log.error('Did not receive a correct complete response: %s. Content %s', complete_response, complete_response.content)
        raise

    return complete_response
