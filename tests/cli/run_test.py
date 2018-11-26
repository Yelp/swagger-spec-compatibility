# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

import mock
import pytest

from swagger_spec_compatibility.cli.run import _Namespace
from swagger_spec_compatibility.cli.run import _print_json_messages
from swagger_spec_compatibility.cli.run import _print_raw_messages
from swagger_spec_compatibility.cli.run import execute
from swagger_spec_compatibility.rules.common import Level
from tests.conftest import DummyWarningRule


@pytest.fixture
def cli_args():
    return mock.Mock(
        spec_set=_Namespace,
        command='execute',
        func=execute,
        rules=('DummyRule',),
        strict=False,
        old_spec='memory://',
        new_spec='memory://',
    )


@pytest.fixture
def warning_message():
    return DummyWarningRule.validation_message('reference')


@pytest.mark.parametrize('json_output', [True, False])
@pytest.mark.parametrize('strict', [True, False])
@mock.patch('swagger_spec_compatibility.cli.run._print_raw_messages', autospec=True)
@mock.patch('swagger_spec_compatibility.cli.run._print_json_messages', autospec=True)
def test_execute(
    mock__print_json_messages, mock__print_raw_messages, capsys,
    cli_args, json_output, mock_SwaggerClient, mock_RuleRegistry, strict,
):
    cli_args.strict = strict
    cli_args.json_output = json_output
    cli_args.rules = ('DummyWarningRule',)
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


def test__print_raw_messages(capsys, warning_message):
    _print_raw_messages(
        messages_by_level={
            Level.INFO: [],
            Level.WARNING: [warning_message],
        },
    )
    out, _ = capsys.readouterr()
    assert out == 'WARNING rules:\n' \
        '\t[TEST_WARNING_MSG] DummyWarningRule : reference' \
        '\n'


def test__print_json_messages(capsys, warning_message):
    _print_json_messages(
        messages_by_level={
            Level.INFO: [],
            Level.WARNING: [warning_message],
        },
    )
    out, _ = capsys.readouterr()
    assert json.loads(out) == {
        'WARNING': [
            {
                'error_code': 'TEST_WARNING_MSG',
                'reference': 'reference',
                'short_name': 'DummyWarningRule',
            },
        ],
    }
