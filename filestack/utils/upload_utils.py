import os
import mimetypes
import multiprocessing
import hashlib
import requests

from base64 import b64encode
from filestack.config import (
    MULTIPART_START_URL, MULTIPART_UPLOAD_URL, MULTIPART_COMPLETE_URL,
    DEFAULT_CHUNK_SIZE, HEADERS
)
from functools import partial
from multiprocessing import Pool


def get_file_info(filepath, filename=None, mimetype=None):
    filename = filename or os.path.split(filepath)[1]
    filesize = os.path.getsize(filepath)
    mimetype = mimetype or mimetypes.guess_type(filepath)[0]
    return filename, filesize, mimetype


def multipart_start(apikey, filename, filesize, mimetype, storage, security=None, params=None):
    data = {
        'apikey': apikey,
        'filename': filename,
        'mimetype': mimetype,
        'size': filesize,
        'store_location': storage
    }
    if security:
        data.update({
            'policy': security['policy'],
            'signature': security['signature']
        })
    response = requests.post(
        MULTIPART_START_URL,
        data=data,
        files={'file': (filename, '', None)},
        params=params,
        headers=HEADERS
    )

    if not response.ok:
        raise Exception(response.text)
    
    return response.json()


def create_upload_jobs(apikey, filename, filepath, filesize, start_response):
    seek_point = 0
    part = 1
    jobs = []
    while seek_point < filesize:
        jobs.append({
            'seek': seek_point,
            'filepath': filepath,
            'filename': filename,
            'apikey': apikey,
            'part': part,
            'uri': start_response['uri'],
            'region': start_response['region'],
            'upload_id': start_response['upload_id']
        })
        part += 1
        seek_point += DEFAULT_CHUNK_SIZE
    return jobs


def upload_chunk(storage, job):

    with open(job['filepath'], 'rb') as f:
        f.seek(job['seek'])
        chunk = f.read(DEFAULT_CHUNK_SIZE)

    data = {
        'apikey': job['apikey'],
        'part': job['part'],
        'size': len(chunk),
        'md5': b64encode(hashlib.md5(chunk).digest()).strip(),
        'uri': job['uri'],
        'region': job['region'],
        'upload_id': job['upload_id'],
        'store_location': storage
    }
    fs_resp = requests.post(
        MULTIPART_UPLOAD_URL,
        data=data,
        files={'file': (job['filename'], '', None)},
        headers=HEADERS
    ).json()

    resp = requests.put(fs_resp['url'], headers=fs_resp['headers'], data=chunk)

    return '{}:{}'.format(job['part'], resp.headers['ETag'])


def multipart_complete(apikey, filename, filesize, mimetype, start_response, storage, parts_and_etags, params=None):
    response = requests.post(
        MULTIPART_COMPLETE_URL,
        data={
            'apikey': apikey,
            'uri': start_response['uri'],
            'region': start_response['region'],
            'upload_id': start_response['upload_id'],
            'filename': filename,
            'size': filesize,
            'mimetype': mimetype,
            'parts': ';'.join(parts_and_etags),
            'store_location': storage
        },
        files={
            'file': (filename, '', None)
        },
        params=params,
        headers=HEADERS
    )
    return response


def multipart_upload(apikey, filepath, storage, upload_processes=None, params=None, security=None):

    if upload_processes is None:
        upload_processes = multiprocessing.cpu_count()

    try:
        filename = params['filename']
    except (KeyError, TypeError):
        filename = None

    try:
        mimetype = params['mimetype']
    except (KeyError, TypeError):
        mimetype = None

    filename, filesize, mimetype = get_file_info(filepath, filename=filename, mimetype=mimetype)

    response_info = multipart_start(apikey, filename, filesize, mimetype, storage, params=params, security=security)
    jobs = create_upload_jobs(apikey, filename, filepath, filesize, response_info)

    pool = Pool(processes=upload_processes)
    pooling_job = partial(upload_chunk, storage)
    parts_and_etags = pool.map(pooling_job, jobs)
    file_data = multipart_complete(apikey, filename, filesize, mimetype, response_info, storage, parts_and_etags, params=params)

    return file_data
