# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import RuleRegistry
from swagger_spec_compatibility.rules.common import ValidationMessage
from tests.conftest import DummyRule


def test_RuleRegistry_rule_names(mock_RuleRegistry):
    assert set(RuleRegistry.rule_names()) == set(mock_RuleRegistry.keys())


def test_RuleRegistry_rules(mock_RuleRegistry):
    assert set(RuleRegistry.rules()) == set(mock_RuleRegistry.values())


def test_RuleRegistry_has_rule_with_real_rules(mock_RuleRegistry):
    assert all(RuleRegistry.has_rule(rule_name) for rule_name in mock_RuleRegistry.keys())


def test_RuleRegistry_rule_with_real_rules(mock_RuleRegistry):
    assert all(rule == RuleRegistry.rule(rule_name) for (rule_name, rule) in mock_RuleRegistry.items())


def test_RuleRegistry_has_rule_with_not_existing_rule(mock_RuleRegistry):
    assert not RuleRegistry.has_rule(mock.Mock())


def test_RuleRegistry_rule_with_not_existing_rule(mock_RuleRegistry):
    with pytest.raises(KeyError):
        RuleRegistry.rule(mock.Mock())


def test_ValidationMessage_string_representation():
    assert ValidationMessage(
        level=Level.ERROR,
        rule=DummyRule,
        reference='reference',
    ).string_representation() == '[TEST_NO_MSG] DummyRule : reference'


def test_initializing_BaseRule_throws_an_exception():
    with pytest.raises(RuntimeError) as excinfo:
        DummyRule()

    assert excinfo.value.args == ('This class should not be initialized. The assumed usage is via class methods.', )
