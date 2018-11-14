# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import mock
import pytest

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import RuleRegistry


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
    error_code = 'TEST_1'
    short_name = 'DummyRule'
    description = 'Rule description'

    def validate(self, old_spec, new_spec):  # pragma: no cover
        return []


class DummyFailRule(BaseRule):
    error_code = 'TEST_2'
    short_name = 'DummyFailRule'
    description = 'Rule description'

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
