#!/usr/bin/env python
from setuptools import setup
import re


def get_version():
    init_py = open('amocrm/__init__.py').read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
    return metadata['version']

version = get_version()


setup(
    name='amocrm_api',
    version=version,
    packages=['amocrm'],
    url='https://github.com/Krukov/amocrm_api',
    download_url='https://github.com/Krukov/amocrm_api/tarball/%s' % version,
    license='MIT license',
    author='Dmitry Krukov',
    author_email='glebov.ru@gmail.com',
    description='Python API for Amocrm',
    long_description=open('README.rst').read(),

    requires=[
        'requests (>=2.3)',
        'responses (>=0.2.2)',
        'six (>=1.7.3)',
        'pytz',
    ],
    install_requires=[
        'requests >=2.3',
        'responses >=0.2.2',
        'six >=1.7.3',
        'pytz',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
