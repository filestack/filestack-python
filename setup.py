import os
import re
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


def read_version():
    with open('filestack/__init__.py') as f:
        return re.search(r'__version__ = \'(.+)\'$', f.readline()).group(1)


setup(
    name='filestack-python',
    version=read_version(),
    license='Apache 2.0',
    description='Filestack REST API Library',
    long_description='Visit: https://github.com/filestack/filestack-python',
    url='https://github.com/filestack/filestack-python',
    author='filestack.com',
    author_email='support@filestack.com',
    packages=find_packages(),
    install_requires=['requests', 'trafaret', 'future'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
