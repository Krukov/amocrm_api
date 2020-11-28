#!/usr/bin/env python
from setuptools import setup, find_packages
import re


def get_version():
    init_py = open('amocrm/__init__.py').read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
    return metadata['version']

version = get_version()


setup(
    name='amocrm_api',
    version=version,
    packages=find_packages(),
    url='https://github.com/Krukov/amocrm_api',
    download_url='https://github.com/Krukov/amocrm_api/tarball/%s' % version,
    license='MIT license',
    author='Dmitry Kryukov',
    author_email='glebov.ru@gmail.com',
    description='Python API for Amocrm',
    long_description=open('README.rst').read(),
    install_requires=[
        'requests',
        'pyjwt',
    ],
    extras_require={
        'cli': ['python-slugify', ],
    },
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'pyamogen=amocrm.v2.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
