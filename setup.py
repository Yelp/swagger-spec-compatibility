# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name='swagger-spec-compatibility',
    version='1.0.1',
    author='Yelp, Inc.',
    author_email='opensource+swagger-spec-compatibility@yelp.com',
    description='Python library to check Swagger Spec backward compatibility',
    long_description=long_description,
    url='https://github.com/Yelp/swagger-spec-compatibility',
    install_requires=[
        'bravado',
        'bravado-core',
        'swagger-spec-validator',
        'six',
        'termcolor',
        'typing_extensions',
    ],
    extras_require={
        ':python_version<"3.5"': ['typing'],
        ':python_version<"3.2"': ['functools32'],
    },
    license='Copyright Yelp, Inc. 2018',
    packages=find_packages(exclude=('tests*', 'testing*')),
    package_data={
        'swagger_spec_compatibility': ['py.typed'],
    },
    entry_points={
        'console_scripts': [
            'swagger_spec_compatibility = swagger_spec_compatibility.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
