# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from swagger_spec_compatibility.__main__ import main
from tests.conftest import DummyRule


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
