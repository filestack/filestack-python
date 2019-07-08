Filestack Classes
=================

Filestack Python SDK allows you to uploads local files, file-like objects and files from external urls.


Client
------
This class is responsible for uploading files (creating Filelinks), converting external urls to Transformation objects, takes url screenshots and returns zipped files (multiple Filelinks).

In order to make calls to the API, you'll need an instance of the Dropbox object. To instantiate, pass in the access token for the account you want to link. (Tip: You can generate an access token for your own account through the App Console).

In order to create a client instance, pass in your Filestack API key. You can also specify which storage should be used for your uploads and provide a Security object to sign all your API calls.


.. code-block:: python
    :linenos:

    from filestack import Client, Security

    security = Security(policy={'expiry': 1594200833, '<YOUR APP SECRET>'})
    cli = Client('<FILESTACK_APIKEY>', storage='gcs', security=security)


Filelink
--------

Filelink object represents a file that whas uploaded to Filestack. A filelink object can be created by uploading a file using Client instance, or by initializing Filelink class with a handle (unique id) of already uploaded file.


.. code-block:: python
    :linenos:

    from filestack import Filelink

    flink = Filelink('sm9IEXAMPLEQuzfJykmA')
    flink.url  # => 'https://cdn.filestackcontent.com/sm9IEXAMPLEQuzfJykmA'


Transformation
--------------

Transformation objects represent the result of image transformation performed on Filelinks or other Transformations (as they can be chained). Unless explicitly stored, no Filelinks are created when image transformations are performed.


.. code-block:: python
    :linenos:

    from filestack import Filelink

    flink = Filelink('sm9IEXAMPLEQuzfJykmA')

    transformation = flink.resize(width=800)
    transformation.url  # => 'https://cdn.filestackcontent.com/resize=width:800/sm9IEXAMPLEQuzfJykmA'

    new_filelink = transformation.store()
    new_filelink.url  # => 'https://cdn.filestackcontent.com/NEW_HANDLE'
