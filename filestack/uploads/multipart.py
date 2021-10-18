import os
import hashlib
import mimetypes
import multiprocessing
import json
from base64 import b64encode, urlsafe_b64encode
from functools import partial
from multiprocessing.pool import ThreadPool

from filestack import config
from filestack.utils import requests


class Chunk:
    def __init__(self, num, seek_point, data=None, filepath=None):
        self.num = num
        self.seek_point = seek_point
        self.data = data
        self.filepath = filepath

    def __repr__(self):
        return '<Chunk part: {}, seek: {}>'.format(self.num, self.seek_point)

    @property
    def bytes(self):
        if self.data:
            return self.data

        with open(self.filepath, 'rb') as f:
            f.seek(self.seek_point)
            data = f.read(config.DEFAULT_CHUNK_SIZE)

        return data


def multipart_request(url, payload, params=None, security=None):
    for key in ('path', 'location', 'region', 'container', 'access'):
        if key in params:
            payload['store'][key] = params[key]

    if security:
        payload.update({
            'policy': security.policy_b64,
            'signature': security.signature
        })

    return requests.post(url, json=payload).json()


def make_chunks(filepath=None, file_obj=None, filesize=None):
    chunks = []
    for num, seek_point in enumerate(range(0, filesize, config.DEFAULT_CHUNK_SIZE)):
        if filepath:
            chunks.append(Chunk(num + 1, seek_point, filepath=filepath))
        else:  # file_obj
            file_obj.seek(seek_point)
            chunks.append(Chunk(num + 1, seek_point, data=file_obj.read(config.DEFAULT_CHUNK_SIZE)))

    if file_obj:
        del file_obj

    return chunks


def upload_chunk(apikey, filename, storage, start_response, security, secure_mode, chunk):
    payload = {
        'apikey': apikey,
        'part': chunk.num,
        'size': len(chunk.bytes),
        'md5': b64encode(hashlib.md5(chunk.bytes).digest()).strip().decode('utf-8'),
        'uri': start_response['uri'],
        'region': start_response['region'],
        'upload_id': start_response['upload_id'],
        'store': {
            'location': storage,
        }
    }

    if security:
        payload.update({
            'policy': security.policy_b64,
            'signature': security.signature
        })

    if secure_mode:
        encoded_payload = urlsafe_b64encode(str.encode(json.dumps(payload))).decode('utf-8')
        url = "{}/{}".format(
            start_response['secure_upload_url'],
            encoded_payload,
        )
        resp = requests.put(url, data=chunk.bytes)
    else:
        url = "{}{}{}".format(
            config.REQUEST_PROTOCOL,
            start_response['location_url'],
            config.MULTIPART_UPLOAD_PATH,
        )
        upload_resp = requests.post(url, json=payload).json()
        resp = requests.put(upload_resp['url'], headers=upload_resp['headers'], data=chunk.bytes)

    return {'part_number': chunk.num, 'etag': resp.headers['ETag']}


def multipart_upload(apikey, filepath, file_obj, storage, params=None, security=None):
    params = params or {}

    upload_processes = multiprocessing.cpu_count()

    if filepath:
        filename = params.get('filename') or os.path.split(filepath)[1]
        mimetype = params.get('mimetype') or mimetypes.guess_type(filepath)[0] or config.DEFAULT_UPLOAD_MIMETYPE
        filesize = os.path.getsize(filepath)
    else:
        filename = params.get('filename', 'unnamed_file')
        mimetype = params.get('mimetype') or config.DEFAULT_UPLOAD_MIMETYPE
        file_obj.seek(0, os.SEEK_END)
        filesize = file_obj.tell()

    payload = {
        'apikey': apikey,
        'filename': filename,
        'mimetype': mimetype,
        'size': filesize,
        'store': {
            'location': storage
        },
        'parts': [],
    }

    chunks = make_chunks(filepath, file_obj, filesize)
    start_response = multipart_request(config.MULTIPART_START_URL, payload, params, security)

    secure_mode = 'secure_upload_url' in start_response

    upload_func = partial(upload_chunk, apikey, filename, storage,
                          start_response, security, secure_mode)

    # In secure mode we uplaod the first part synchronously.
    if secure_mode:
        payload['parts'] = [upload_func(chunks[0])]
        chunks = chunks[1:]

    # Upload the rest of chunks.
    with ThreadPool(upload_processes) as pool:
        uploaded_parts = pool.map(upload_func, chunks)

    location_url = start_response.pop('location_url')
    payload.update(start_response)
    payload['parts'] += uploaded_parts

    if 'workflows' in params:
        payload['store']['workflows'] = params.pop('workflows')

    if 'upload_tags' in params:
        payload['upload_tags'] = params.pop('upload_tags')

    complete_url = "{}{}{}".format(
        config.REQUEST_PROTOCOL,
        location_url,
        config.MULTIPART_COMPLETE_PATH,
    )
    complete_response = multipart_request(complete_url, payload, params, security)
    return complete_response
