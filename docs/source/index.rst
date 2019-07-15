filestack-python
================

This is the official Python SDK for `Filestack <https://filestack.com>`_ - API and content management system that makes it easy to add powerful file uploading and transformation capabilities to any web or mobile application.

.. code-block:: python

   from filestack import Client

   cli = Client('<FILESTACK APIKEY>')
   filelink = cli.upload(filepath='/path/to/image.jpg')
   print(filelink.url)  # => 'https://cdn.filestackcontent.com/<FILE_HANDLE>'


Table of Contents
-----------------

.. toctree::

   Installation & Quickstart <installation>
   Uploading files <uploading_files>
   API Reference <api_reference>
