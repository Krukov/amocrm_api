#!/usr/bin/env python
from setuptools import setup

setup(
    name='amocrm_api',
    version='0.1.0',
    packages=['amocrm'],
    url='https://github.com/Krukov/amocrm_api',
    download_url='https://github.com/Krukov/amocrm_api/tarball/0.1',
    license='MIT license',
    author='Dmitry Krukov',
    author_email='frog-king69@yandex.ru',
    description='Python (Django like) API for Amocrm',
    long_description=open('README.rst').read(),

    requires=[
        'requests (>=2.3)',
        'responses (>=0.2.2)',
        'six (>=1.7.3)',
    ],
    install_requires=[
        'requests >=2.3',
        'responses >=0.2.2',
        'six >=1.7.3',
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
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
