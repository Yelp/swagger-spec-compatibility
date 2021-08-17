# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing

import pytest

from swagger_spec_compatibility.rules import compatibility_status
from swagger_spec_compatibility.rules import RuleProtocol
from swagger_spec_compatibility.rules import ValidationMessage
from swagger_spec_compatibility.rules.common import RuleRegistry
from tests.conftest import DummyRule
from tests.conftest import DummyRuleFailIfDifferent


def test_compatibility_status_returns_no_issues_if_same_specs_default_parameters(
    mock_RuleRegistry_empty, minimal_spec,
):
    mock_RuleRegistry_empty['DummyRule'] = DummyRule
    mock_RuleRegistry_empty['DummyRuleFailIfDifferent'] = DummyRuleFailIfDifferent
    expected_result = {
        rule: []
        for rule in RuleRegistry.rules()
    }  # type: typing.Mapping[typing.Type[RuleProtocol], typing.Iterable[ValidationMessage]]
    result = compatibility_status(
        old_spec=minimal_spec,
        new_spec=minimal_spec,
    )
    assert result == expected_result


@pytest.mark.parametrize(
    'rules, expected_result',
    [
        (
            (DummyRule,), {DummyRule: []},
        ),
    ],
)
def test_compatibility_status_returns_no_issues_if_same_specs_defined_rules(
    mock_RuleRegistry, minimal_spec, rules, expected_result,
):
    result = compatibility_status(
        old_spec=minimal_spec,
        new_spec=minimal_spec,
        rules=rules,
    )
    assert result == expected_result
