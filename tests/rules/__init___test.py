# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import typing  # noqa: F401

import pytest
from bravado_core.spec import Spec

from swagger_spec_compatibility.rules import BaseRule  # noqa: F401
from swagger_spec_compatibility.rules import compatibility_status
from swagger_spec_compatibility.rules import ValidationMessage  # noqa: F401
from swagger_spec_compatibility.rules.common import RuleRegistry
from tests.conftest import DummyRule
from tests.conftest import DummyRuleFailIfDifferent


def test_compatibility_status_returns_no_issues_if_same_specs_default_parameters(
    mock_RuleRegistry_empty, minimal_spec_dict,
):
    mock_RuleRegistry_empty['DummyRule'] = DummyRule()
    mock_RuleRegistry_empty['DummyRuleFailIfDifferent'] = DummyRuleFailIfDifferent()
    spec = Spec.from_dict(minimal_spec_dict)
    expected_result = {
        rule: []
        for rule in RuleRegistry.rules()
    }  # type: typing.Mapping[typing.Type[BaseRule], typing.Iterable[ValidationMessage]]
    result = compatibility_status(
        old_spec=spec,
        new_spec=spec,
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
    mock_RuleRegistry, minimal_spec_dict, rules, expected_result,
):
    spec = Spec.from_dict(minimal_spec_dict)
    result = compatibility_status(
        old_spec=spec,
        new_spec=spec,
        rules=rules,
    )
    assert result == expected_result
