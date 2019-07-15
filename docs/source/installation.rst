Installation & Quickstart
=========================

`filestack-python` can be installed from PyPI:


.. code-block:: sh

    $ pip install filestack-python

or directly from GitHub:

.. code-block:: sh

    $ pip install git+https://github.com/filestack/filestack-python.git


To upload a file, all you need to do is to create an instance of :class:`filestack.Client` with your Filestack API Key and use the :py:meth:`upload()` method:

.. code-block:: python
    :linenos:

    from filestack import Client

    cli = Client('<FILESTACK_APIKEY>')
    filelink = cli.upload(filepath='path/to/video.mp4')


Proceed :doc:`uploading_files` to section to learn more about file uploaing options. 
