import os
import sys
import mimetypes
import hashlib
import logging
import time

from multiprocessing import Queue, Process
from base64 import b64encode
from collections import deque, OrderedDict

import requests

from filestack.config import HEADERS
from filestack.utils.utils import store_params

log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s - %(processName)s[%(process)d] - %(levelname)s - %(message)s"))
log.addHandler(handler)

UPLOAD_HOST = 'https://upload.filestackapi.com'
MB = 1024 ** 2
DEFAULT_PART_SIZE = 8 * MB
DEFAULT_CHUNK_SIZE = 8 * MB
NUM_OF_UPLOADERS = 4
NUM_OF_COMMITTERS = 2
MAX_DELAY = 4


class ResponseNotOk(Exception):
    pass


class S3UploadException(Exception):
    pass


class UploadManager(object):

    def __init__(self, apikey, filepath, storage, params, security, upload_q, commit_q, response_q):
        self.chunk_size = DEFAULT_CHUNK_SIZE
        self.apikey = apikey
        self.filepath = filepath
        self.storage = storage
        self.params = params
        self.security = security
        self.upload_q = upload_q
        self.commit_q = commit_q
        self.response_q = response_q
        self.filename = os.path.split(filepath)[1]
        self.filesize = os.path.getsize(filepath)
        self.mimetype = mimetypes.guess_type(filepath)[0]
        self.start_response = None
        self.parts = OrderedDict()
        self._currently_processed = 0

    def run(self):
        self._multipart_start()
        self._create_parts()
        self._manage_upload_process()

    def _multipart_start(self):
        data = {
            'apikey': self.apikey,
            'filename': self.filename,
            'mimetype': self.mimetype,
            'size': self.filesize,
            'store_location': self.storage,
            'multipart': True
        }

        if self.params:
            data.update(store_params(self.params))

        if self.security:
            data.update({
                'policy': self.security['policy'],
                'signature': self.security['signature']
            })

        response = requests.post(
            UPLOAD_HOST + '/multipart/start',
            data=data,
            files={'file': (self.filename, '', None)},
            params=self.params,
            headers=HEADERS
        )
        self.start_response = response.json()

    def _multipart_complete(self):
        response_code = 0
        data = {
            'apikey': self.apikey,
            'uri': self.start_response['uri'],
            'region': self.start_response['region'],
            'upload_id': self.start_response['upload_id'],
            'filename': self.filename,
            'size': self.filesize,
            'mimetype': self.mimetype,
            'multipart': True,
            'store_location': self.storage
        }

        if self.params:
            data.update(store_params(self.params))

        while response_code != 200:
            log.info('Waiting for complete')
            response = requests.post(
                UPLOAD_HOST + '/multipart/complete',
                data=data,
                files={'file': (self.filename, '', None)},
                params=self.params,
                headers=HEADERS
            )

            if not response.ok:
                log.error('Unexpected backend response: %s', response.content)
                raise Exception(response.content)

            response_code = response.status_code
            log.info('Got response %s, %s', response, response.content)

        self.response_q.put(response)

    def _create_parts(self):
        for index, seek_point in enumerate(
                self._get_byte_ranges(self.filesize, DEFAULT_PART_SIZE)):

            chunks = deque()
            for ch in self._get_byte_ranges(seek_point['size'], self.chunk_size):
                chunks.appendleft({'offset': ch['seek'], 'size': ch['size']})

            self.parts[index + 1] = {
                'seek': seek_point['seek'],
                'size': seek_point['size'],
                'currently_processed': 0,
                'chunks': chunks
            }

    def _split_chunk(self, chunk):
        return [
            {'offset': ch['seek'], 'size': ch['size']}
            for ch in self._get_byte_ranges(chunk['size'], self.chunk_size, start=chunk['offset'])
        ]

    def _get_next_chunk(self):
        for part_num in self.parts:
            if self.parts[part_num]['chunks']:
                return part_num, self.parts[part_num]['chunks'].pop()
        return None, None

    def _feed_uploaders(self):
        while self._currently_processed < NUM_OF_UPLOADERS:
            part_num, chunk = self._get_next_chunk()

            if not chunk:
                break

            if chunk['size'] > self.chunk_size:
                smaller_chunks = self._split_chunk(chunk)
                chunk, rest = smaller_chunks[0], smaller_chunks[1:]

                for c in reversed(rest):
                    self.parts[part_num]['chunks'].append(c)

            self._submit_upload_job(part_num, chunk)

    def _manage_upload_process(self):
        self._feed_uploaders()

        while self.parts:
            response = self.response_q.get(block=True)
            log.info('Got response %s', response)

            if response['worker'] == 'uploader':
                self.parts[response['part']]['currently_processed'] -= 1
                self._currently_processed -= 1
                old_chunk = response['chunk']

                if not response['success']:
                    log.warning('Failed response received %s', response)

                    if response['delay']:
                        # this means uploader got a response, but it wasn't ok (status code >= 400)
                        # resubmit with requested delay if max delay not exceeded
                        if response['delay'] > MAX_DELAY:
                            log.error('Max delay exceeded for chunk %s', old_chunk)
                            return
                        self._submit_upload_job(response['part'], old_chunk, delay=response['delay'])
                        continue

                    if old_chunk['size'] <= self.chunk_size:
                        log.info(
                            'Failed to upload %s bytes. Changing chunk size from %s to %s bytes',
                            old_chunk['size'], self.chunk_size, self.chunk_size / 2
                        )
                        self.chunk_size /= 2

                        if self.chunk_size < 32 * 1024:
                            log.error('Minimal chunk size failed')
                            return

                    new_chunks = self._split_chunk(old_chunk)
                    for new_chunk in reversed(new_chunks):
                        self.parts[response['part']]['chunks'].append(new_chunk)

                    self._feed_uploaders()
                    continue

                if not self.parts[response['part']]['chunks'] and self.parts[response['part']]['currently_processed'] == 0:
                    log.info('No more chunks for part %s, time to commit', response['part'])
                    self.commit_q.put({
                        'apikey': self.apikey,
                        'uri': self.start_response['uri'],
                        'region': self.start_response['region'],
                        'upload_id': self.start_response['upload_id'],
                        'size': self.filesize,
                        'part': response['part'],
                        'store_location': self.storage,
                        'filename': self.filename,
                    })

                self._feed_uploaders()

            elif response['worker'] == 'committer':
                log.info('Got commit done message %s', response)
                log.info('Removing part %s', response['part'])
                self.parts.pop(response['part'])

        if self._get_next_chunk()[1] is None:
            self._multipart_complete()

    def _submit_upload_job(self, part_num, chunk, delay=0):
        self.upload_q.put({
            'chunk': chunk,
            'apikey': self.apikey,
            'store_location': self.storage,
            'part': part_num,
            'seek': self.parts[part_num]['seek'],
            'offset': chunk['offset'],
            'size': chunk['size'],
            'filepath': self.filepath,
            'filename': self.filename,
            'filesize': self.filesize,
            'uri': self.start_response['uri'],
            'region': self.start_response['region'],
            'upload_id': self.start_response['upload_id'],
            'delay': delay
        })
        self.parts[part_num]['currently_processed'] += 1
        self._currently_processed += 1

    @staticmethod
    def _get_byte_ranges(filesize, part_size, start=0, bytes_to_read=None):
        if bytes_to_read is None:
            bytes_to_read = filesize

        ranges = []
        pos = start

        while bytes_to_read > 0:
            point = {'seek': pos}
            if bytes_to_read > part_size:
                size = part_size
                bytes_to_read -= part_size
                pos += part_size
            else:
                size = bytes_to_read
                bytes_to_read = 0
            point['size'] = size
            ranges.append(point)

        return ranges


def manage_upload(apikey, filepath, storage, params, security, upload_q, commit_q, response_q):
    manager = UploadManager(apikey, filepath, storage, params, security, upload_q, commit_q, response_q)
    manager.run()


def consume_upload_job(upload_q, response_q):
    log.info('Uploader ready')
    while True:
        job = upload_q.get(block=True)

        if job == 'die':
            break  # we need a way to stop it in tests (other than terminate())

        log.info(
            'Uploader got chunk %s for part %s',
            job['chunk'], job['part']
        )
        log.debug('Job details: %s', job)

        delay = job.get('delay', 0)
        time.sleep(delay)
        log.info('Uploader waiting for %s seconds', delay)

        with open(job['filepath'], 'rb') as f:
            f.seek(job['seek'] + job['offset'])
            chunk = f.read(job['size'])

        success = True
        try:
            backend_resp = requests.post(
                UPLOAD_HOST + '/multipart/upload',
                data={
                    'apikey': job['apikey'],
                    'part': job['part'],
                    'size': job['size'],
                    'md5': b64encode(hashlib.md5(chunk).digest()).strip(),
                    'uri': job['uri'],
                    'region': job['region'],
                    'upload_id': job['upload_id'],
                    'store_location': job['store_location'],
                    'multipart': True,
                    'offset': job['offset']
                },
                files={'file': (job['filename'], '', None)},
                headers=HEADERS
            )
            if not backend_resp.ok:
                raise ResponseNotOk('Incorrect backend response %s', backend_resp)

            backend_data = backend_resp.json()
            try:
                s3_resp = requests.put(
                    backend_data['url'],
                    headers=backend_data['headers'],
                    data=chunk
                )
            except Exception as e:
                log.warning('Upload to S3 failed %s', e)
                raise S3UploadException(str(e))

            if not s3_resp.ok:
                raise ResponseNotOk('Incorrect S3 response %s', s3_resp)

        except ResponseNotOk:
            delay = delay * 1.3 or 1
            success = False
        except S3UploadException:
            delay = 0
            success = False
        except Exception as e:
            delay = 0
            log.error('Request to backend failed %s', e)
            success = False

        response_q.put({
            'worker': 'uploader',
            'chunk': job['chunk'],
            'part': job['part'],
            'offset': job['offset'],
            'size': job['size'],
            'success': success,
            'delay': delay
        })

        log.info(
            'Uploader finished chunk %s for part %s. Success: %s',
            job['chunk'], job['part'], success
        )


def commit_part(commit_q, response_q):
    log.info('Committer ready')
    while True:
        job = commit_q.get(block=True)

        if job == 'die':
            break  # we need a way to stop it in tests (other than terminate())

        log.info('Committer got job for part %s', job['part'])
        log.debug('Job details: %s', job)

        requests.post(
            UPLOAD_HOST + '/multipart/commit',
            data={
                'apikey': job['apikey'],
                'uri': job['uri'],
                'region': job['region'],
                'upload_id': job['upload_id'],
                'size': job['size'],
                'part': job['part'],
                'store_location': job['store_location']
            },
            files={'file': (job['filename'], '', None)},
            headers=HEADERS
        )

        response_q.put({
            'worker': 'committer',
            'success': True,
            'part': job['part']
        })
        log.info('Commit job done')


def upload(apikey, filepath, storage, params=None, security=None):
    upload_q = Queue()
    commit_q = Queue()
    response_q = Queue()

    manager_proc = Process(
        target=manage_upload,
        name='manager',
        args=(apikey, filepath, storage, params, security, upload_q, commit_q, response_q)
    )

    side_processes = [
        Process(
            target=consume_upload_job,
            name='uploader',
            args=(upload_q, response_q)
        ) for _ in range(NUM_OF_UPLOADERS)
    ]

    for _ in range(NUM_OF_COMMITTERS):
        side_processes.append(
            Process(
                target=commit_part,
                name='committer',
                args=(commit_q, response_q)
            )
        )

    for proc in side_processes:
        proc.start()

    manager_proc.start()
    manager_proc.join()

    for proc in side_processes:
        proc.terminate()

    try:
        final_response = response_q.get(block=True, timeout=1)
        if not isinstance(final_response, requests.Response):
            raise Exception()
        return final_response
    except Exception:
        raise Exception('Upload aborted')
