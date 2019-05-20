import os
import mimetypes
import multiprocessing
import hashlib
import requests

from base64 import b64encode
from filestack.config import (
    MULTIPART_START_URL, DEFAULT_CHUNK_SIZE, DEFAULT_UPLOAD_MIMETYPE, HEADERS
)
from filestack.utils.utils import store_params
from functools import partial
from multiprocessing.pool import ThreadPool


def get_file_info(filepath, filename=None, mimetype=None):
    filename = filename or os.path.split(filepath)[1]
    filesize = os.path.getsize(filepath)
    mimetype = mimetype or mimetypes.guess_type(filepath)[0] or DEFAULT_UPLOAD_MIMETYPE
    return filename, filesize, mimetype


def multipart_request(url, data, params=None, security=None):

    if params:
        data.update(store_params(params))

    if security:
        data.update({
            'policy': security['policy'],
            'signature': security['signature']
        })

    response = requests.post(
        url,
        data=data,
        files={'file': (data['filename'], '', None)},
        headers=HEADERS
    )

    if not response.ok:
        raise Exception('Invalid API response')

    return response.json()


def create_upload_jobs(filesize):
    seek_point = 0
    part = 1
    jobs = []
    while seek_point < filesize:
        jobs.append({
            'seek': seek_point,
            'part': part,
        })
        part += 1
        seek_point += DEFAULT_CHUNK_SIZE
    return jobs


def upload_chunk(apikey, filename, filepath, storage, start_response, job):
    with open(filepath, 'rb') as f:
        f.seek(job['seek'])
        chunk = f.read(DEFAULT_CHUNK_SIZE)

    data = {
        'apikey': apikey,
        'part': job['part'],
        'size': len(chunk),
        'md5': b64encode(hashlib.md5(chunk).digest()).strip(),
        'uri': start_response['uri'],
        'region': start_response['region'],
        'upload_id': start_response['upload_id'],
        'store_location': storage
    }
    fs_resp = requests.post(
        'https://{}/multipart/upload'.format(start_response['location_url']),
        data=data,
        files={'file': (filename, '', None)},
        headers=HEADERS
    ).json()

    resp = requests.put(fs_resp['url'], headers=fs_resp['headers'], data=chunk)

    return '{}:{}'.format(job['part'], resp.headers['ETag'])


def multipart_upload(apikey, filepath, storage, upload_processes=None, params=None, security=None):
    params = params or {}

    if upload_processes is None:
        upload_processes = multiprocessing.cpu_count()

    filename = params.get('filename')
    mimetype = params.get('mimetype')

    filename, filesize, mimetype = get_file_info(filepath, filename=filename, mimetype=mimetype)

    request_data = {
        'apikey': apikey,
        'filename': filename,
        'mimetype': mimetype,
        'size': filesize,
        'store_location': storage
    }

    start_response = multipart_request(MULTIPART_START_URL, request_data, params, security)
    jobs = create_upload_jobs(filesize)

    pooling_job = partial(upload_chunk, apikey, filename, filepath, storage, start_response)
    pool = ThreadPool(upload_processes)
    uploaded_parts = pool.map(pooling_job, jobs)
    pool.close()

    location_url = start_response.pop('location_url')
    request_data.update(start_response)
    request_data['parts'] = ';'.join(uploaded_parts)

    if params.get('workflows'):
        workflows = ','.join('"{}"'.format(item) for item in params.get('workflows'))
        workflows = '[{}]'.format(workflows)
        request_data['workflows'] = workflows

    complete_response = multipart_request(
        'https://{}/multipart/complete'.format(location_url),
        request_data,
        params,
        security
    )

    return complete_response
