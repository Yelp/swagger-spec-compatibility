# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os

import mock
import pytest

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import RuleRegistry
from swagger_spec_compatibility.rules.common import RuleType
from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict


REPO_ROOT = os.path.dirname(os.path.dirname(__file__))


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
def minimal_spec(minimal_spec_dict):
    return load_spec_from_spec_dict(minimal_spec_dict)


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
    error_level = Level.ERROR
    description = 'Rule description'
    rule_type = RuleType.MISCELLANEOUS
    short_name = 'DummyRule'

    @classmethod
    def validate(cls, left_spec, right_spec):  # pragma: no cover
        return ()


class DummyInfoRule(BaseRule):
    error_code = 'TEST_INFO_MSG'
    error_level = Level.INFO
    description = 'Rule description'
    rule_type = RuleType.MISCELLANEOUS
    short_name = 'DummyInfoRule'

    @classmethod
    def validate(cls, left_spec, right_spec):  # pragma: no cover
        return (cls.validation_message('test'),)


class DummyWarningRule(BaseRule):
    error_code = 'TEST_WARNING_MSG'
    error_level = Level.WARNING
    description = 'Rule description'
    rule_type = RuleType.MISCELLANEOUS
    short_name = 'DummyWarningRule'

    @classmethod
    def validate(cls, left_spec, right_spec):  # pragma: no cover
        return (cls.validation_message('test'),)


class DummyRuleFailIfDifferent(BaseRule):
    error_code = 'TEST_FAIL_IF_DIFFERENT'
    error_level = Level.ERROR
    description = 'Rule description'
    rule_type = RuleType.MISCELLANEOUS
    short_name = 'DummyRuleFailIfDifferent'

    @classmethod
    def validate(cls, left_spec, right_spec):  # pragma: no cover
        return (cls.validation_message('test'),) if left_spec != right_spec else ()


class DummyErrorRule(BaseRule):
    error_code = 'TEST_ERROR_MSG'
    error_level = Level.ERROR
    description = 'Rule description'
    rule_type = RuleType.MISCELLANEOUS
    short_name = 'DummyErrorRule'

    @classmethod
    def validate(cls, left_spec, right_spec):  # pragma: no cover
        return (cls.validation_message('test'),)


class DummyRuleWithDocumentationLink(BaseRule):
    error_code = 'TEST_DOCUMENTATION_LINK'
    error_level = Level.INFO
    description = 'Rule description'
    rule_type = RuleType.MISCELLANEOUS
    short_name = 'DummyRuleWithDocLink'
    documentation_link = 'link'

    @classmethod
    def validate(cls, left_spec, right_spec):  # pragma: no cover
        return ()


MOCKED_RULE_REGISTRY = {
    'DummyRule': DummyRule,
    'DummyInfoRule': DummyInfoRule,
    'DummyWarningRule': DummyWarningRule,
    'DummyErrorRule': DummyErrorRule,
    'DummyRuleFailIfDifferent': DummyRuleFailIfDifferent,
}


@pytest.fixture
def mock_RuleRegistry():
    with mock.patch.object(
        RuleRegistry, '_REGISTRY', MOCKED_RULE_REGISTRY,
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
