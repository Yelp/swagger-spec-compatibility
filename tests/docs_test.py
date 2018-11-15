# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
from glob import iglob
from itertools import chain

import pytest


@pytest.fixture(scope='session')
def repository_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope='session')
def docs_dir(repository_root):
    print(repository_root)
    return os.path.join(repository_root, 'docs', 'source')


@pytest.fixture(scope='session')
def package_root(repository_root):
    return os.path.join(repository_root, 'swagger_spec_compatibility')


@pytest.fixture(scope='session')
def source_files(package_root):
    return set(chain(
        iglob(os.path.join(package_root, '*.py')),
        iglob(os.path.join(package_root, '**', '*.py')),
    ))


BLACKLIST_MODULES_FROM_DOCUMENTATION = {
    'swagger_spec_compatibility.__main__',
}


def _from_path_to_module(package_root, path):
    return '{lib}.{module}'.format(
        lib=os.path.basename(package_root),
        module=os.path.relpath(path, package_root).replace('.py', '').replace(os.sep, '.'),
    ).replace('.__init__', '')


def _contain_docstring_or_code(path):
    with open(path) as f:
        lines_with_no_comments = (
            re.sub('(#.*)', '', line.rstrip())
            for line in f.readlines()
        )
        not_empty_lines = (
            line
            for line in lines_with_no_comments
            if line.strip()
        )
        return any(not_empty_lines)


@pytest.fixture(scope='session')
def python_modules(package_root, source_files):
    modules = {
        _from_path_to_module(package_root, source_file)
        for source_file in source_files
        if _contain_docstring_or_code(source_file)
    }
    return modules - BLACKLIST_MODULES_FROM_DOCUMENTATION


@pytest.fixture(scope='session')
def doc_files(docs_dir):
    return set(chain(
        iglob(os.path.join(docs_dir, '*.md')),
        iglob(os.path.join(docs_dir, '**', '**.md')),
        iglob(os.path.join(docs_dir, '*.rst')),
        iglob(os.path.join(docs_dir, '**', '**.rst')),
    ))


def get_documented_modules(doc_file):
    regex = re.compile('\\.\\.\\sautomodule::\\s+(?P<module>[^\\s]+)')
    with open(doc_file) as f:
        for line in f.readlines():
            m = regex.search(line)
            if m:
                yield m.group(str('module'))


@pytest.fixture(scope='session')
def documented_modules(doc_files):
    return {
        documented_module
        for file in doc_files
        for documented_module in get_documented_modules(file)
    }


def test_ensure_all_modules_are_available_in_documentation(python_modules, documented_modules):
    not_documented_modules = python_modules - documented_modules
    assert not not_documented_modules, \
        'The following modules are not available in documentation. ' \
        'Add them to documentation or to BLACKLIST_MODULES_FROM_DOCUMENTATION: {}'.format(
            ', '.join(sorted(not_documented_modules)),
        )


def test_ensure_all_documented_modules_are_from_this_library(python_modules, documented_modules):
    documented_modules_not_in_source = documented_modules - python_modules
    assert not documented_modules_not_in_source, \
        'The following modules are available in documentation but not in source code. ' \
        'Remove them from documentation or make sure that the code is available: {}'.format(
            ', '.join(sorted(documented_modules_not_in_source)),
        )
