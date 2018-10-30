# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from setuptools import find_packages
from setuptools import setup


setup(
    name='swagger-spec-compatibility',
    version='0.0.1',
    author='Yelp, Inc.',
    author_email='opensource+swagger-spec-compatibility@yelp.com',
    install_requires=[
        'bravado-core',
    ],
    extras_require={
        ':python_version<"3.5"': ['typing'],
    },
    license='Copyright Yelp, Inc. 2018',
    packages=find_packages(exclude=('tests*', 'testing*')),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
