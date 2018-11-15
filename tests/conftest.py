# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import RuleRegistry
from swagger_spec_compatibility.rules.common import ValidationMessage


@pytest.fixture
def minimal_spec_dict():
    return {
        'swagger': '2.0',
        'info': {
            'version': '1.0.0',
            'title': 'Minimal Swagger spec',
        },
        'schemes': ['http'],
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'paths': {},
        'definitions': {},
    }


@pytest.fixture
def simple_operation_dict():
    return {
        'responses': {
            '200': {
                'description': '',
            },
        },
    }


class DummyRule(BaseRule):
    error_code = 'TEST_NO_MSG'
    short_name = 'DummyRule'
    description = 'Rule description'

    @classmethod
    def validate(cls, old_spec, new_spec):  # pragma: no cover
        return ()


class DummyInfoRule(BaseRule):
    error_code = 'TEST_INFO_MSG'
    short_name = 'DummyInfoRule'
    description = 'Rule description'

    @classmethod
    def validate(cls, old_spec, new_spec):  # pragma: no cover
        return (
            ValidationMessage(
                level=Level.INFO,
                rule=cls,
                reference='test',
            ),
        )


class DummyWarningRule(BaseRule):
    error_code = 'TEST_WARNING_MSG'
    short_name = 'DummyWarningRule'
    description = 'Rule description'

    @classmethod
    def validate(cls, old_spec, new_spec):  # pragma: no cover
        return (
            ValidationMessage(
                level=Level.WARNING,
                rule=cls,
                reference='test',
            ),
        )


class DummyRuleFailIfDifferent(BaseRule):
    error_code = 'TEST_NO_MSG'
    short_name = 'DummyRuleFailIfDifferent'
    description = 'Rule description'

    @classmethod
    def validate(cls, old_spec, new_spec):  # pragma: no cover
        return (
            ValidationMessage(
                level=Level.ERROR,
                rule=cls,
                reference='test',
            ),
        ) if old_spec != new_spec else ()


class DummyErrorRule(BaseRule):
    error_code = 'TEST_ERROR_MSG'
    short_name = 'DummyErrorRule'
    description = 'Rule description'

    @classmethod
    def validate(cls, old_spec, new_spec):  # pragma: no cover
        return (
            ValidationMessage(
                level=Level.ERROR,
                rule=cls,
                reference='test',
            ),
        )


@pytest.fixture
def mock_RuleRegistry():
    with mock.patch.object(
            RuleRegistry, '_REGISTRY', {
                'DummyRule': DummyRule,
                'DummyInfoRule': DummyInfoRule,
                'DummyWarningRule': DummyWarningRule,
                'DummyErrorRule': DummyErrorRule,
                'DummyRuleFailIfDifferent': DummyRuleFailIfDifferent,
            },
    ) as m:
        yield m


@pytest.fixture
def mock_RuleRegistry_empty():
    with mock.patch.object(RuleRegistry, '_REGISTRY', {}) as m:
        yield m


@pytest.fixture
def mock_SwaggerClient():
    with mock.patch('swagger_spec_compatibility.spec_utils.SwaggerClient', autospec=True) as m:
        yield m
