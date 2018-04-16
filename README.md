<p align="center"><img src="logo.svg" align="center" width="100"/></p>
<h1 align="center">Filestack Python</h1>
<p align="center">
  <a href="http://travis-ci.org/filestack/filestack-python">
    <img src="https://img.shields.io/travis/filestack/filestack-python.svg">
  </a>
  <a href="https://pypi.python.org/pypi/filestack-python/2.3.1">
    <img src="https://img.shields.io/pypi/v/filestack-python.svg">
  </a>
</p>
This is the official Python SDK for Filestack - API and content management system that makes it easy to add powerful file uploading and transformation capabilities to any web or mobile application.

## Resources

* [API Reference](https://filestack.github.io/filestack-python)

## Installing

Install ``filestack`` with pip

```shell
pip install filestack-python
```

or directly from GitHub

```shell
pip install git+https://github.com/filestack/filestack-python.git
```

## Usage

The Filestack SDK allows you to upload and handle filelinks using two main classes: Client and Filelink.

### Uploading New File with Client
``` python
from filestack import Client
client = Client("<YOUR_API_KEY>")

params = {'mimetype': 'image/png'}
new_filelink = client.upload(filepath="path/to/file", params=params)
print(new_filelink.url)
```
Uploading local files will use Filestack's multipart upload by default. To disable, just set the argument to false.

```python
new_filelink = client.upload(filepath="path/to/file", multipart=False)
```
#### Uploading files using Filestack Intelligent Ingestion
To upload files using Filestack Intelligent Ingestion, simply add `intelligent=True` argument
```python
new_filelink = client.upload(filepath="path/to/file", intelligent=True)
```
FII always uses multipart uploads. In case of network issues, it will dynamically split file parts into smaller chunks (sacrificing upload speed in favour of upload reliability).

### Create Filelink using Existing Handle
```python
from filestack import Filelink
new_filelink = Filelink("<YOUR_HANDLE>")
```

### Basic Filelink Functions

With a Filelink, you can download to a local path or get the content of a file. You can also delete or overwrite files if you have security enabled on your account.

```python
file_content = new_filelink.get_content()

response = new_filelink.download("/path/to/file")

filelink.overwrite(filepath="path/to/new/file")

response = filelink.delete()
```

### Transformations

You can chain transformations on both Filelinks and external URLs. Storing transformations will return a new Filelink object.

```python
transform = client.transform_external('http://<SOME_URL>')
new_filelink = transform.resize(width=500, height=500).flip().enhance().store()

filelink = Filelink("<YOUR_HANDLE">)
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

Security is set on Client or Filelink classes upon instantiation.

```python
from filestack import security

json_policy = {"expiry": 253381964415}
security = security(json_policy, '<YOUR_APP_SECRET>')
client = Client("<YOUR_API_KEY", security=security)

# new Filelink object inherits security and will use for all calls
new_filelink = client.upload(filepath="path/to/file")
```

## Versioning

Filestack Python SDK follows the [Semantic Versioning](http://semver.org/).
