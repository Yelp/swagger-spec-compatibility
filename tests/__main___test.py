# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import mock
import pytest

from swagger_spec_compatibility.__main__ import main
from swagger_spec_compatibility.rules import BaseRule
from swagger_spec_compatibility.rules import RuleRegistry


class DummyRule(BaseRule):
    def description(self):
        return 'Rule description'

    def validate(self, old_spec, new_spec):  # pragma: no cover
        return None


class DummyFailRule(BaseRule):
    def description(self):
        return 'Rule description'

    def validate(self, old_spec, new_spec):  # pragma: no cover
        return None


@pytest.fixture
def mock_RuleRegistry():
    with mock.patch.object(RuleRegistry, '_REGISTRY', {'DummyRule': DummyRule()}) as m:
        yield m


@pytest.fixture
def mock_RuleRegistry_empty():
    with mock.patch.object(RuleRegistry, '_REGISTRY', {}) as m:
        yield m


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


@mock.patch('swagger_spec_compatibility.rules.SwaggerClient', autospec=True)
def test_main_run_succeed(mock_SwaggerClient, mock_RuleRegistry, capsys):
    assert main(['run', __file__, __file__]) == 0
    capsys.readouterr()
