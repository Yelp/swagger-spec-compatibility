# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import sys
from glob import iglob
from itertools import chain
from subprocess import CalledProcessError
from subprocess import check_call

import pytest


BLACKLIST_MODULES_FROM_DOCUMENTATION = {
    'swagger_spec_compatibility.__main__',
}


def _extract_documented_models(doc_file):
    regex = re.compile('\\.\\.\\sautomodule::\\s+(?P<module>[^\\s]+)')
    with open(doc_file) as f:
        for line in f.readlines():
            m = regex.search(line)
            if m:
                yield m.group(str('module'))


def _from_path_to_module(PACKAGE_DIR, path):
    return '{lib}.{module}'.format(
        lib=os.path.basename(PACKAGE_DIR),
        module=os.path.relpath(path, PACKAGE_DIR).replace('.py', '').replace(os.sep, '.'),
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


REPOSITORY_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOC_DIR = os.path.join(REPOSITORY_ROOT, 'docs', 'source')
PACKAGE_DIR = os.path.join(REPOSITORY_ROOT, 'swagger_spec_compatibility')
SOURCE_FILES = set(chain(
    iglob(os.path.join(PACKAGE_DIR, '*.py')),
    iglob(os.path.join(PACKAGE_DIR, '**', '*.py')),
))
PYTHON_MODULES = {
    _from_path_to_module(PACKAGE_DIR, source_file)
    for source_file in SOURCE_FILES
    if _contain_docstring_or_code(source_file)
} - BLACKLIST_MODULES_FROM_DOCUMENTATION
DOC_FILES = set(chain(
    iglob(os.path.join(DOC_DIR, '*.md')),
    iglob(os.path.join(DOC_DIR, '**', '**.md')),
    iglob(os.path.join(DOC_DIR, '*.rst')),
    iglob(os.path.join(DOC_DIR, '**', '**.rst')),
))
DOCUMENTED_MODULES = {
    documented_module
    for file in DOC_FILES
    for documented_module in _extract_documented_models(file)
}
BACKWARD_INCOMPATIBILITY_TESTERS = sorted(
    iglob(os.path.join(DOC_DIR, 'rules', 'examples', '*', 'tester.py')),
)


def test_ensure_all_modules_are_available_in_documentation():
    not_documented_modules = PYTHON_MODULES - DOCUMENTED_MODULES
    assert not not_documented_modules, \
        'The following modules are not available in documentation. ' \
        'Add them to documentation or to BLACKLIST_MODULES_FROM_DOCUMENTATION: {}'.format(
            ', '.join(sorted(not_documented_modules)),
        )


@pytest.mark.parametrize(
    'backward_incompatibility_tester',
    BACKWARD_INCOMPATIBILITY_TESTERS,
)
def test_backward_incompatibility_testers_are_not_failing(backward_incompatibility_tester):
    try:
        check_call(
            [sys.executable, backward_incompatibility_tester],
            cwd=os.path.dirname(backward_incompatibility_tester),
        )
    except CalledProcessError:  # pragma: no cover
        pytest.fail('{} has failed to run.'.format(backward_incompatibility_tester))
