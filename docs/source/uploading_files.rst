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
