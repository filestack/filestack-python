<p align="center"><img src="logo.svg" align="center" width="100"/></p>
<h1 align="center">Filestack Python</h1>
<p align="center">
  <a href="http://travis-ci.org/filestack/filestack-python">
    <img src="https://img.shields.io/travis/filestack/filestack-python.svg">
  </a>
  <a href="https://pypi.python.org/pypi/filestack-python">
    <img src="https://img.shields.io/pypi/v/filestack-python.svg">
  </a>
    <img src="https://img.shields.io/pypi/pyversions/filestack-python.svg">
</p>
This is the official Python SDK for Filestack - API and content management system that makes it easy to add powerful file uploading and transformation capabilities to any web or mobile application.

## Resources

To learn more about this SDK, please visit our API Reference

* [API Reference](https://filestack-python.readthedocs.io)

## Installing

Install ``filestack`` with pip

```shell
pip install filestack-python
```

or directly from GitHub

```shell
pip install git+https://github.com/filestack/filestack-python.git
```

## Quickstart

The Filestack SDK allows you to upload and handle filelinks using two main classes: Client and Filelink.

### Uploading files with `filestack.Client`
``` python
from filestack import Client
client = Client('<YOUR_API_KEY>')

new_filelink = client.upload(filepath='path/to/file')
print(new_filelink.url)
```

#### Uploading files using Filestack Intelligent Ingestion
To upload files using Filestack Intelligent Ingestion, simply add `intelligent=True` argument
```python
new_filelink = client.upload(filepath='path/to/file', intelligent=True)
```
FII always uses multipart uploads. In case of network issues, it will dynamically split file parts into smaller chunks (sacrificing upload speed in favour of upload reliability).

### Working with Filelinks
Filelink objects can by created by uploading new files, or by initializing `filestack.Filelink` with already existing file handle
```python
from filestack import Filelink, Client

client = Client('<APIKEY>')
filelink = client.upload(filepath='path/to/file')
filelink.url  # 'https://cdn.filestackcontent.com/FILE_HANDLE

# work with previously uploaded file
filelink = Filelink('FILE_HANDLE')
```

### Basic Filelink Functions

With a Filelink, you can download to a local path or get the content of a file. You can also perform various transformations.

```python
file_content = new_filelink.get_content()

size_in_bytes = new_filelink.download('/path/to/file')

filelink.overwrite(filepath='path/to/new/file')

filelink.resize(width=400).flip()

filelink.delete()
```

### Transformations

You can chain transformations on both Filelinks and external URLs. Storing transformations will return a new Filelink object.

```python
transform = client.transform_external('http://<SOME_URL>')
new_filelink = transform.resize(width=500, height=500).flip().enhance().store()

filelink = Filelink('<YOUR_HANDLE'>)
new_filelink = filelink.resize(width=500, height=500).flip().enhance().store()
```

You can also retrieve the transformation url at any point.

 ```python
transform_candidate = client.transform_external('http://<SOME_URL>')
transform = transform_candidate.resize(width=500, height=500).flip().enhance()
print(transform.url)
```

### Audio/Video Convert

Audio and video conversion works just like any transformation, except it returns an instance of class AudioVisual, which allows you to check the status of your video conversion, as well as get its UUID and timestamp. 

```python
av_object = filelink.av_convert(width=100, height=100)
while (av_object.status != 'completed'):
    print(av_object.status)
    print(av_object.uuid)
    print(av_object.timestamp)
```

The status property makes a call to the API to check its current status, and you can call to_filelink() once video is complete (this function checks its status first and will fail if not completed yet).

```python
filelink = av_object.to_filelink()
```

### Security Objects

Security is set on Client or Filelink classes upon instantiation and is used to sign all API calls.

```python
from filestack import Security

policy = {'expiry': 253381964415}  # 'expiry' is the only required key
security = Security(policy, '<YOUR_APP_SECRET>')
client = Client('<YOUR_API_KEY', security=security)

# new Filelink object inherits security and will use for all calls
new_filelink = client.upload(filepath='path/to/file')

# you can also provide Security objects explicitly for some methods
size_in_bytes = filelink.download(security=security)
```

You can also retrieve security details straight from the object:
```python
>>> policy = {'expiry': 253381964415, 'call': ['read']}
>>> security = Security(policy, 'SECURITY-SECRET')
>>> security.policy_b64
'eyJjYWxsIjogWyJyZWFkIl0sICJleHBpcnkiOiAyNTMzODE5NjQ0MTV9'
>>> security.signature
'f61fa1effb0638ab5b6e208d5d2fd9343f8557d8a0bf529c6d8542935f77bb3c'
```

### Webhook verification

You can use `filestack.helpers.verify_webhook_signature` method to make sure that the webhooks you receive are sent by Filestack.

```python
from filestack.helpers import verify_webhook_signature

# webhook_data is raw content you receive
webhook_data = b'{"action": "fp.upload", "text": {"container": "some-bucket", "url": "https://cdn.filestackcontent.com/Handle", "filename": "filename.png", "client": "Computer", "key": "key_filename.png", "type": "image/png", "size": 1000000}, "id": 50006}'

result, details = verify_webhook_signature(
    '<YOUR_WEBHOOK_SECRET>',
    webhook_data,
    {
      'FS-Signature': '<SIGNATURE-FROM-REQUEST-HEADERS>',
      'FS-Timestamp': '<TIMESTAMP-FROM-REQUEST-HEADERS>'
    }
)

if result is True:
    print('Webhook is valid and was generated by Filestack')
else:
    raise Exception(details['error'])
```

## Versioning

Filestack Python SDK follows the [Semantic Versioning](http://semver.org/).
