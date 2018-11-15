# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import mock

from swagger_spec_compatibility.cli.run import _Namespace
from swagger_spec_compatibility.cli.run import execute


def test_execute(mock_SwaggerClient, mock_RuleRegistry):
    execute(
        mock.Mock(
            spec_set=_Namespace,
            command='execute',
            func=execute,
            rules=('DummyRule',),
            strict=False,
            old_spec='memory://',
            new_spec='memory://',
        ),
    )
