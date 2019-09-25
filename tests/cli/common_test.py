# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
from argparse import ArgumentTypeError

import mock
import pytest

from swagger_spec_compatibility.cli.common import CLIRulesProtocol
from swagger_spec_compatibility.cli.common import pre_process_cli_to_discover_rules
from swagger_spec_compatibility.cli.common import rules
from swagger_spec_compatibility.cli.common import uri
from tests.conftest import DummyRule


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


@pytest.mark.parametrize(
    'cli_rules, cli_blacklist_rules, expected_rules',
    [
        [('DummyRule',), (), {DummyRule}],
        [('DummyRule',), ('DummyRule',), set()],
        [(), ('DummyRule',), set()],
    ],
)
def test_rules(mock_RuleRegistry, cli_rules, cli_blacklist_rules, expected_rules):
    assert rules(
        mock.Mock(
            spec=CLIRulesProtocol,
            rules=cli_rules,
            blacklist_rules=cli_blacklist_rules,
        ),
    ) == expected_rules


@pytest.mark.parametrize(
    'env_variable_content, argv, import_module_calls',
    [
        ['', [], []],
        [
            'a.not.existing.module',
            [],
            [mock.call('a.not.existing.module')],
        ],
        [
            'a.not.existing.module,a.not.existing.module.1',
            [],
            [mock.call('a.not.existing.module'), mock.call('a.not.existing.module.1')],
        ],
        ['', ['-d=a.not.existing.module'], [mock.call('a.not.existing.module')]],
        [
            '',
            ['-d=a.not.existing.module', '-d=a.not.existing.module.1'],
            [mock.call('a.not.existing.module'), mock.call('a.not.existing.module.1')],
        ],
        [
            '',
            ['-d', 'a.not.existing.module', 'a.not.existing.module.1'],
            [mock.call('a.not.existing.module'), mock.call('a.not.existing.module.1')],
        ],
        [
            '',
            ['-d', 'a.not.existing.module', '--discover-rules-from', 'a.not.existing.module.1'],
            [mock.call('a.not.existing.module'), mock.call('a.not.existing.module.1')],
        ],
        [
            'a.not.existing.module.environment',
            ['-d', 'a.not.existing.module', '--discover-rules-from', 'a.not.existing.module.1'],
            [mock.call('a.not.existing.module'), mock.call('a.not.existing.module.1'), mock.call('a.not.existing.module.environment')],
        ],
    ],
)
@mock.patch('swagger_spec_compatibility.cli.common.Scanner', autospec=True)
@mock.patch('swagger_spec_compatibility.cli.common.import_module', autospec=True)
def test_pre_process_cli_to_discover_rules(mock_import_module, mock_scanner, env_variable_content, argv, import_module_calls):
    with mock.patch.dict(os.environ, {'CUSTOM_RULE_PACKAGES': env_variable_content}):
        pre_process_cli_to_discover_rules(argv)

    assert mock_import_module.call_count == len(import_module_calls)
    assert mock_scanner.return_value.scan.call_count == len(import_module_calls)

    mock_import_module.assert_has_calls(import_module_calls, any_order=True)


def test_pre_process_cli_to_discover_rules_warns_if_the_module_does_not_exist():
    with pytest.warns(
        RuntimeWarning,
        match='\'a.module.that.does.not.exist\' module, specified via the rule discovery CLI, is not found. Ignoring it.',
    ):
        pre_process_cli_to_discover_rules(['-d', 'a.module.that.does.not.exist'])
