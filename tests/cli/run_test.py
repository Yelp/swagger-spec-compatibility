# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from swagger_spec_compatibility.cli.run import _Namespace
from swagger_spec_compatibility.cli.run import _print_raw_messages
from swagger_spec_compatibility.cli.run import _print_validation_messages
from swagger_spec_compatibility.cli.run import execute
from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import ValidationMessage
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
    return ValidationMessage(
        level=Level.WARNING,
        rule=DummyWarningRule,
        reference='reference',
    )


@pytest.mark.parametrize(
    'strict', [True, False],
)
def test_execute(cli_args, mock_SwaggerClient, mock_RuleRegistry, strict):
    cli_args.strict = strict
    cli_args.rules = ('DummyWarningRule',)
    assert execute(cli_args) == (1 if strict else 0)


def test__print_raw_messages(capsys, warning_message):
    _print_raw_messages(
        level=Level.WARNING,
        messages=[warning_message],
    )
    out, _ = capsys.readouterr()
    assert out == 'WARNING rules:\n' \
        '\t[TEST_WARNING_MSG] DummyWarningRule : reference' \
        '\n'


@mock.patch('swagger_spec_compatibility.cli.run._print_raw_messages', autospec=True)
def test__print_validation_messages(mock__print_raw_messages, capsys, cli_args, warning_message):
    _print_validation_messages(
        cli_args=cli_args,
        messages_by_level={
            Level.INFO: [],
            Level.WARNING: [warning_message],
        },
    )
    mock__print_raw_messages.assert_called_once_with(
        level=Level.WARNING,
        messages=[warning_message],
    )
