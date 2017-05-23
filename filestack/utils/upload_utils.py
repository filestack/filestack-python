import os
import mimetypes
import hashlib
import requests

from filestack.config import MULTIPART_START_URL, MULTIPART_UPLOAD_URL, MULTIPART_COMPLETE_URL, DEFAULT_CHUNK_SIZE
from functools import partial
from multiprocessing import Pool


def get_file_info(filepath):
    filename = os.path.split(filepath)[1]
    filesize = os.path.getsize(filepath)
    mimetype = mimetypes.guess_type(filepath)[0]
    return filename, filesize, mimetype


def multipart_start(apikey, filename, filesize, mimetype, storage):
    response = requests.post(
            MULTIPART_START_URL, files={'file': (filename, '', None)},
            data={
                'apikey': apikey,
                'filename': filename,
                'mimetype': mimetype,
                'size': filesize,
                'store_location': storage
                }
            )
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
        'md5': hashlib.md5(chunk).digest().encode('base64').strip(),
        'uri': job['uri'],
        'region': job['region'],
        'upload_id': job['upload_id'],
        'store_location': storage
    }

    fs_resp = requests.post(
        MULTIPART_UPLOAD_URL,
        data=data,
        files={
            'file': (job['filename'], '', None)
        }
    ).json()

    resp = requests.put(
        fs_resp['url'],
        headers=fs_resp['headers'],
        data=chunk
    )
    return '{}:{}'.format(job['part'], resp.headers['ETag'])


def multipart_complete(apikey, filename, filesize, mimetype, start_response, storage, parts_and_etags):
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
    )
    return response


def multipart_upload(apikey, filepath, storage):
    filename, filesize, mimetype = get_file_info(filepath)
    response_info = multipart_start(apikey, filename, filesize, mimetype, storage)
    jobs = create_upload_jobs(apikey, filename, filepath, filesize, response_info)

    pool = Pool(processes=4)
    pooling_job = partial(upload_chunk, storage)
    parts_and_etags = pool.map(pooling_job, jobs)
    file_data = multipart_complete(apikey, filename, filesize, mimetype, response_info, storage, parts_and_etags)

    return file_data