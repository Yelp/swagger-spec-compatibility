# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest


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
