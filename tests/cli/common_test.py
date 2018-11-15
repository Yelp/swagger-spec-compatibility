# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
from argparse import ArgumentTypeError

import pytest

from swagger_spec_compatibility.cli.common import uri


@pytest.mark.parametrize(
    'param, expected_result',
    [
        pytest.param(
            __file__, 'file://{}'.format(os.path.abspath(__file__)),
            marks=pytest.mark.skipif(
                condition=sys.platform == 'win32',
                reason='Absolute paths on Windows works differently respect OSX and Linux',
            ),
        ),
        pytest.param(
            # TODO: It will fail for now, once I have a Windows machine I'll fix it
            __file__, 'file://{}'.format(os.path.abspath(__file__)),
            marks=pytest.mark.skipif(
                condition=sys.platform != 'win32',
                reason='Absolute paths on Windows works differently respect OSX and Linux',
            ),
        ),
        ('schema://path.domain', 'schema://path.domain'),
    ],
)
def test_uri(param, expected_result):
    assert uri(param) == expected_result


def test_uri_raises_if_path_does_not_exists(tmpdir):
    with pytest.raises(ArgumentTypeError):
        uri(os.path.join(tmpdir.strpath, str('not-existing-file')))
