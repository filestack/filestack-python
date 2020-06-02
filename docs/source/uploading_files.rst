Uploading files
===============

Filestack Python SDK allows you to uploads local files, file-like objects and files from external urls.


Local files
-----------

.. code-block:: python
    :linenos:

    from filestack import Client

    cli = Client('<FILESTACK_APIKEY>')
    filelink = cli.upload(filepath='path/to/video.mp4')

    # upload to non-default storage provider under specific path
    store_params = {
        'location': 'gcs',  # Google Cloud Storage
        'path': 'folder/subfolder/video_file.mpg'
    }
    filelink = cli.upload(filepath='path/to/video.mp4', store_params=store_params)


File-like objects
-----------------

.. code-block:: python
    :linenos:

    from filestack import Client

    cli = Client('<FILESTACK_APIKEY>')
    with open('path/to/video.mp4', 'rb') as f:
        filelink = cli.upload(file_obj=f)


To upload in-memory bytes:

.. code-block:: python
    :linenos:

    import io
    from filestack import Client

    bytes_to_upload = b'content'

    cli = Client('<FILESTACK_APIKEY>')
    filelink = cli.uploads(file_obj=io.BytesIO(bytes_to_upload))


External urls
-------------

.. code-block:: python
    :linenos:

    from filestack import Client

    cli = Client('<FILESTACK_APIKEY>')
    filelink = cli.upload_url(url='https://f4fcdn.eu/wp-content/uploads/2018/06/krakowmain.jpg')


Store params
------------

Each upload function shown above takes a :data:`store_params` argument which is a Python dictionary with following keys (all are optional):

.. code-block:: python
    :linenos:

    store_params = {
        'filename': 'string',
        'location': 'string',
        'path': 'string',
        'container': 'string',
        'mimetype': 'string',
        'region': 'string',
        'access': 'string',
        'base64decode': True|False,
        'workflows': ['workflow-id-1', 'workflow-id-2'],
        'upload_tags': {
            'key': 'value',
            'key2': 'value'
        }
    }

* **filename** - name for the stored file
* **location** - storage provider to be used
* **path** - the path to store the file within the specified container
* **container** - the bucket or container (folder) in which to store the file (does not apply when storing to Dropbox)
* **mimetype** - mime type that should be stored in file's metadata
* **region** - storage region (applies to S3 only)
* **access** - should the file be stored as :data:`"public"` or :data:`"private"` (applies to S3 only)
* **base64decode** - indicates if content should be decoded before it is stored
* **workflows** - IDs of `Filestack Workflows <https://www.filestack.com/products/workflows>`_ that should be triggered after upload
* **upload_tags** - set of :data:`key: value` pairs that will be returned with webhook for particular upload
