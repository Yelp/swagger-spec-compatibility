# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy

import mock
import pytest

from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict
from swagger_spec_compatibility.util import EntityMapping
from swagger_spec_compatibility.walkers.enum_values import _different_enum_values_mapping
from swagger_spec_compatibility.walkers.enum_values import EnumValuesDiff
from swagger_spec_compatibility.walkers.enum_values import EnumValuesDifferWalker


@pytest.mark.parametrize(
    'left_dict, right_dict, expected_value',
    [
        (None, None, None),
        ({}, {}, None),
        ({'type': 'object'}, {}, None),
        ({'enum': ['v1']}, {}, None),
        ({'type': 'string', 'enum': ['v1']}, {}, EntityMapping({'v1'}, set())),
        ({}, {'type': 'string', 'enum': ['v1']}, EntityMapping(set(), {'v1'})),
        ({'type': 'string', 'enum': ['v1']}, {'type': 'string', 'enum': ['v1']}, None),
        ({'type': 'string', 'enum': ['v1', 'v2']}, {'type': 'string', 'enum': ['v2', 'v1']}, None),
        ({'type': 'string', 'enum': ['old', 'common']}, {'type': 'string', 'enum': ['common', 'new']}, EntityMapping({'old'}, {'new'})),
    ],
)
def test__different_enum_values_mapping(left_dict, right_dict, expected_value):
    assert _different_enum_values_mapping(
        left_spec=mock.sentinel.LEFT_SPEC,
        right_spec=mock.sentinel.RIGHT_SPEC,
        left_schema=left_dict,
        right_schema=right_dict,
    ) == expected_value


def test_EnumValuesDifferWalker_returns_no_paths_if_no_endpoints_defined(minimal_spec):
    assert EnumValuesDifferWalker(minimal_spec, minimal_spec).walk() == []


def test_EnumValuesDifferWalker_returns_paths_of_endpoints_responses(minimal_spec_dict):
    old_spec_dict = dict(
        minimal_spec_dict,
        definitions={
            'enum_1': {
                'type': 'string',
                'enum': ['value_to_remove', 'E2', 'E3'],
                'x-model': 'enum_1',
            },
            'enum_2': {
                'type': 'string',
                'enum': ['E1', 'E2', 'E3'],
                'x-model': 'enum_2',
            },
            'object': {
                'properties': {
                    'enum_1': {'$ref': '#/definitions/enum_1'},
                    'enum_2': {'$ref': '#/definitions/enum_2'},
                },
                'type': 'object',
                'x-model': 'object',
            },
        },
        paths={
            '/endpoint': {
                'get': {
                    'parameters': [{
                        'in': 'body',
                        'name': 'body',
                        'required': True,
                        'schema': {
                            '$ref': '#/definitions/object',
                        },
                    }],
                    'responses': {
                        '200': {
                            'description': '',
                            'schema': {
                                '$ref': '#/definitions/object',
                            },
                        },
                    },
                },
            },
        },
    )
    new_spec_dict = deepcopy(old_spec_dict)
    del new_spec_dict['definitions']['enum_1']['enum'][0]
    new_spec_dict['definitions']['enum_2']['enum'].append('new_value')
    old_spec = load_spec_from_spec_dict(old_spec_dict)
    new_spec = load_spec_from_spec_dict(new_spec_dict)

    assert sorted(EnumValuesDifferWalker(old_spec, new_spec).walk()) == sorted([
        EnumValuesDiff(
            path=('definitions', 'enum_2'),
            mapping=EntityMapping(old=set(), new={'new_value'}),
        ),
        EnumValuesDiff(
            path=('definitions', 'object', 'properties', 'enum_2'),
            mapping=EntityMapping(old=set(), new={'new_value'}),
        ),
        EnumValuesDiff(
            path=('definitions', 'object', 'properties', 'enum_1'),
            mapping=EntityMapping(old={'value_to_remove'}, new=set()),
        ),
        EnumValuesDiff(
            path=('definitions', 'enum_1'),
            mapping=EntityMapping(old={'value_to_remove'}, new=set()),
        ),
        EnumValuesDiff(
            path=('paths', '/endpoint', 'get', 'responses', '200', 'schema', 'properties', 'enum_2'),
            mapping=EntityMapping(old=set(), new={'new_value'}),
        ),
        EnumValuesDiff(
            path=('paths', '/endpoint', 'get', 'responses', '200', 'schema', 'properties', 'enum_1'),
            mapping=EntityMapping(old={'value_to_remove'}, new=set()),
        ),
        EnumValuesDiff(
            path=('paths', '/endpoint', 'get', 'parameters', 0, 'schema', 'properties', 'enum_2'),
            mapping=EntityMapping(old=set(), new={'new_value'}),
        ),
        EnumValuesDiff(
            path=('paths', '/endpoint', 'get', 'parameters', 0, 'schema', 'properties', 'enum_1'),
            mapping=EntityMapping(old={'value_to_remove'}, new=set()),
        ),
    ])
