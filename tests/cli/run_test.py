# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json
import os
from collections import namedtuple

import mock
import pytest

from swagger_spec_compatibility.cli.common import uri
from swagger_spec_compatibility.cli.run import _Namespace
from swagger_spec_compatibility.cli.run import _print_json_messages
from swagger_spec_compatibility.cli.run import _print_raw_messages
from swagger_spec_compatibility.cli.run import execute
from swagger_spec_compatibility.rules.changed_type import ChangedType
from swagger_spec_compatibility.rules.common import Level
from tests.conftest import DummyWarningRule


# Need to use a namedtuple instead of mock because these
# args are used in multiprocessing and thus need to be
# serializable with pickle (mock is not)
MockCLIArgs = namedtuple(
    'MockCLIArgs', [
        'spec_set',
        'command',
        'func',
        'rules',
        'blacklist_rules',
        'strict',
        'old_spec',
        'new_spec',
        'json_output',
    ],
)


@pytest.fixture
def cli_args():
    return MockCLIArgs(
        spec_set=_Namespace,
        command='execute',
        func=execute,
        rules=('DummyRule',),
        blacklist_rules=(),
        strict=False,
        old_spec='memory://',
        new_spec='memory://',
        json_output=False,
    )


@pytest.fixture
def warning_message():
    return DummyWarningRule.validation_message('reference')


@pytest.fixture
def error_message_library_rule():
    return ChangedType.validation_message('reference')


@pytest.mark.parametrize('json_output', [True, False])
@pytest.mark.parametrize('strict', [True, False])
@mock.patch('swagger_spec_compatibility.cli.run._print_raw_messages', autospec=True)
@mock.patch('swagger_spec_compatibility.cli.run._print_json_messages', autospec=True)
def test_execute(
    mock__print_json_messages, mock__print_raw_messages, capsys,
    cli_args, json_output, mock_RuleRegistry, strict, tmpdir, minimal_spec_dict,
):
    spec_path = str(os.path.join(tmpdir.strpath, 'swagger.json'))
    with open(spec_path, 'w') as f:
        json.dump(minimal_spec_dict, f)
    cli_args = cli_args._replace(strict=strict)
    cli_args = cli_args._replace(json_output=json_output)
    cli_args = cli_args._replace(rules=('DummyWarningRule',))
    cli_args = cli_args._replace(old_spec=uri(spec_path))
    cli_args = cli_args._replace(new_spec=uri(spec_path))
    assert execute(cli_args) == (1 if strict else 0)
    if json_output:
        mock__print_json_messages.assert_called_once_with({
            Level.INFO: mock.ANY,
            Level.WARNING: mock.ANY,
            Level.ERROR: mock.ANY,
        })
        assert not mock__print_raw_messages.called
    else:
        mock__print_raw_messages.assert_called_once_with({
            Level.INFO: mock.ANY,
            Level.WARNING: mock.ANY,
            Level.ERROR: mock.ANY,
        })
        assert not mock__print_json_messages.called
    capsys.readouterr()


def test__print_raw_messages(capsys, warning_message, error_message_library_rule):
    _print_raw_messages(
        messages_by_level={
            Level.INFO: [],
            Level.WARNING: [warning_message],
            Level.ERROR: [error_message_library_rule],
        },
    )
    out, _ = capsys.readouterr()
    assert out == 'WARNING rules:\n' \
                  '\t[TEST_WARNING_MSG] DummyWarningRule: reference\n' \
                  'ERROR rules:\n' \
                  '\t[MIS-E002] Changed type: reference (documentation: ' \
                  'https://swagger-spec-compatibility.readthedocs.io/en/latest/rules/MIS-E002.html)' \
                  '\n'


def test__print_json_messages(capsys, warning_message, error_message_library_rule):
    _print_json_messages(
        messages_by_level={
            Level.INFO: [],
            Level.WARNING: [warning_message],
            Level.ERROR: [error_message_library_rule],
        },
    )
    out, _ = capsys.readouterr()
    assert json.loads(out) == {
        'WARNING': [
            {
                'error_code': 'TEST_WARNING_MSG',
                'reference': 'reference',
                'short_name': 'DummyWarningRule',
                'documentation': None,
            },
        ],
        'ERROR': [
            {
                'documentation': 'https://swagger-spec-compatibility.readthedocs.io/en/latest/rules/MIS-E002.html',
                'error_code': 'MIS-E002',
                'reference': 'reference',
                'short_name': 'Changed type',
            },
        ],
    }
