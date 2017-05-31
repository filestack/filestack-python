[![Travis CI][travis_ci_badge]][travis_ci]
[![Coveralls][coveralls_badge]][coveralls]
[![Code Climate][code_climate_badge]][code_climate]

# Filestack Python SDK
<a href="https://www.filestack.com"><img src="https://filestack.com/themes/filestack/assets/images/press-articles/color.svg" align="left" hspace="10" vspace="6"></a>
This is the official Python SDK for Filestack - API and content management system that makes it easy to add powerful file uploading and transformation capabilities to any web or mobile application.

## Resources

* [Filestack](https://www.filestack.com)
* [Documentation](https://www.filestack.com/docs)
* [API Reference](https://filestack.github.io/)

## Installing

Install ``filestack`` with pip

    $ pip install filestack

or directly from GitHub

    $ pip install git+https://github.com/filestack/filestack-python.git

## Usage

The Filestack SDK allows you to upload and handle filelinks using two main classes: Client and Filelink.

### Uploading New File with Client

    $ from filestack import Client
    $ client = Client("<YOUR_API_KEY>")
     
    $ params = {'mimetype': 'image/png'}
    $ new_filelink = client.upload(filepath="path/to/file", params=params)
    
Uploading local files will use Filestack's multipart upload by default. To disable, just set the argument to false.

    $ new_filelink = client.upload(filepath="path/to/file", multipart=False)

### Create Filelink using Existing Handle

    $ from filestack import Filelink
    $ new_filelink = Filelink("<YOUR_HANDLE>")
    
### Basic Filelink Functions

With a Filelink, you can download to a local path or get the content of a file. You can also delete or overwrite files if you have security enabled on your account. 

    $ file_content = new_filelink.get_content()

### Transformations

You can chain transformations on both Filelinks and external URLS. Storing transformations will return a new Filelink object.

    $ transform = client.transform_external('http://<SOME_URL>')
    $ new_filelink = transform.resize(width=500, height=500).store()
    
    $ filelink = Filelink("<YOUR_HANDLE">)
    # new_filelink = filelink.resize(width=500, height=500).store()

## Versioning

Filestack Python SDK follows the [Semantic Versioning](http://semver.org/).

## Issues

If you have problems, please create a [Github Issue](https://github.com/filepicker/filestack-python/issues).

## Contributing

Please see [CONTRIBUTING.md](https://github.com/filepicker/filestack-python/CONTRIBUTING.md) for details.

## Credits

Thank you to all the [contributors](https://github.com/filepicker/filestack-python/graphs/contributors).


## Installing

[travis_ci]: http://travis-ci.org/filestack/filestack-python
[travis_ci_badge]: https://travis-ci.org/filestack/filestack-python.svg?branch=master
[code_climate]: https://codeclimate.com/github/filestack/filestack-python
[code_climate_badge]: https://codeclimate.com/github/filestack/filestack-python.png
[coveralls]: https://coveralls.io/github/filestack/filestack-python?branch=master
[coveralls_badge]: https://coveralls.io/repos/github/filestack/filestack-python/badge.svg?branch=master
