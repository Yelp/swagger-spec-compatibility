# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from swagger_spec_compatibility import cli
from swagger_spec_compatibility.__main__ import main
from swagger_spec_compatibility.cli.common import add_rules_arguments
from tests.conftest import DummyRule
from tests.conftest import MOCKED_RULE_REGISTRY


def test_main_fails_with_no_command(capsys):
    with pytest.raises(SystemExit):
        main([])
    capsys.readouterr()


def test_main_fails_if_no_rule_defined(mock_RuleRegistry_empty, capsys):
    with pytest.raises(SystemExit):
        main([])
    capsys.readouterr()


def test_main_explain_succeed(mock_RuleRegistry, capsys):
    assert main(['explain']) == 0
    out, _ = capsys.readouterr()
    assert 'Rules explanation' in out
    assert 'DummyRule' in out
    assert 'Rule description' in out


def test_main_run_succeed(mock_SwaggerClient, mock_RuleRegistry_empty, capsys):
    mock_RuleRegistry_empty['DummyRule'] = DummyRule
    assert main(['run', __file__, __file__]) == 0
    capsys.readouterr()


@pytest.mark.parametrize(
    'cli_args, expected_rules, expected_blacklist_rules',
    [
        # Default values
        [['test'], MOCKED_RULE_REGISTRY.keys(), []],
        # Rules
        [['test', '-r', 'DummyRule'], ['DummyRule'], []],
        [['test', '-r', 'DummyRule', 'DummyRule'], ['DummyRule'], []],
        [['test', '-r', 'DummyRule', 'DummyErrorRule'], ['DummyRule', 'DummyErrorRule'], []],
        [['test', '-r', 'DummyRule', '-r', 'DummyErrorRule'], ['DummyRule', 'DummyErrorRule'], []],

        # Blacklist rules
        [['test', '-b', 'DummyRule'], MOCKED_RULE_REGISTRY.keys(), ['DummyRule']],
        [['test', '-b', 'DummyRule', 'DummyRule'], MOCKED_RULE_REGISTRY.keys(), ['DummyRule']],
        [['test', '-b', 'DummyRule', 'DummyErrorRule'], MOCKED_RULE_REGISTRY.keys(), ['DummyRule', 'DummyErrorRule']],
        [['test', '-b', 'DummyRule', '-b', 'DummyErrorRule'], MOCKED_RULE_REGISTRY.keys(), ['DummyRule', 'DummyErrorRule']],
    ],
)
def test_post_process_rules_cli_arguments(mock_RuleRegistry, cli_args, expected_rules, expected_blacklist_rules):
    def add_sub_parser(subparsers):
        explain_parser = subparsers.add_parser('test')
        add_rules_arguments(explain_parser)
        return explain_parser

    execute_function = mock.Mock(name='test associated function')

    with mock.patch.object(
        cli, '_SUB_COMMAND_ASSOCIATED_FUNCTION_MAPPING',
        {add_sub_parser: execute_function},
    ):
        main(cli_args)

    args = execute_function.call_args.args[0]
    assert args.func == execute_function
    assert set(args.rules) == set(expected_rules)
    assert set(args.blacklist_rules) == set(expected_blacklist_rules)
