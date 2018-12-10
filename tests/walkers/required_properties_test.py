# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict
from swagger_spec_compatibility.util import EntityMapping
from swagger_spec_compatibility.walkers.required_properties import _different_properties_mapping
from swagger_spec_compatibility.walkers.required_properties import RequiredPropertiesDiff
from swagger_spec_compatibility.walkers.required_properties import RequiredPropertiesDifferWalker


@pytest.mark.parametrize(
    'left_required_properties, right_required_properties, expected_value',
    [
        (set(), set(), None),
        ({'property'}, {'property'}, None),
        (set(), {'property'}, EntityMapping(set(), {'property'})),
        ({'property'}, set(), EntityMapping({'property'}, set())),
        ({'property', 'old'}, {'property'}, EntityMapping({'old'}, set())),
        ({'property'}, {'property', 'new'}, EntityMapping(set(), {'new'})),
        ({'property', 'old'}, {'property', 'new'}, EntityMapping({'old'}, {'new'})),
    ],
)
@mock.patch('swagger_spec_compatibility.walkers.required_properties.get_required_properties', autospec=True)
def test__different_properties_mapping(
        mock_get_required_properties, left_required_properties, right_required_properties, expected_value,
):
    mock_get_required_properties.side_effect = [
        left_required_properties,
        right_required_properties,
    ]

    assert _different_properties_mapping(
        left_spec=mock.sentinel.LEFT_SPEC,
        right_spec=mock.sentinel.RIGHT_SPEC,
        left_schema=mock.sentinel.LEFT_SCHEMA,
        right_schema=mock.sentinel.RIGHT_SCHEMA,
    ) == expected_value

    assert mock_get_required_properties.call_count == 2
    mock_get_required_properties.assert_has_calls(
        calls=[
            mock.call(schema=mock.sentinel.LEFT_SCHEMA, swagger_spec=mock.sentinel.LEFT_SPEC),
            mock.call(schema=mock.sentinel.RIGHT_SCHEMA, swagger_spec=mock.sentinel.RIGHT_SPEC),

        ],
        any_order=False,
    )


@pytest.mark.parametrize(
    'left_schema, right_schema, expected_diffs',
    [
        ({}, {}, []),
        (
            {
                'properties': {
                    'old_only': {'type': 'string'},
                },
                'required': ['old_only'],
                'type': 'object',
            },
            {},
            [RequiredPropertiesDiff(path=('definitions', 'model'), mapping=EntityMapping(old={'old_only'}, new=set()))],
        ),
        (
            {},
            {
                'properties': {
                    'new_only': {'type': 'string'},
                },
                'required': ['new_only'],
                'type': 'object',
            },
            [RequiredPropertiesDiff(path=('definitions', 'model'), mapping=EntityMapping(old=set(), new={'new_only'}))],
        ),
        (
            {
                'properties': {
                    'common': {
                        'type': 'object',
                        'properties': {
                            'nested_common': {'type': 'string'},
                            'nested_old_only': {'type': 'string'},
                        },
                        'required': ['nested_common', 'nested_old_only'],
                    },
                    'only_old': {'type': 'string'},
                },
                'required': ['common', 'only_old'],
                'type': 'object',
            },
            {
                'properties': {
                    'common': {
                        'type': 'object',
                        'properties': {
                            'nested_common': {'type': 'string'},
                            'nested_new_only': {'type': 'string'},
                        },
                        'required': ['nested_common', 'nested_new_only'],
                    },
                    'only_new': {'type': 'string'},
                },
                'required': ['common', 'only_new'],
                'type': 'object',
            },
            [
                RequiredPropertiesDiff(
                    path=('definitions', 'model'),
                    mapping=EntityMapping(old={'only_old'}, new={'only_new'}),
                ),
                RequiredPropertiesDiff(
                    path=('definitions', 'model', 'properties', 'common'),
                    mapping=EntityMapping(old={'nested_old_only'}, new={'nested_new_only'}),
                ),
            ],
        ),
    ],
)
def test_RequiredPropertiesDifferWalker(minimal_spec_dict, left_schema, right_schema, expected_diffs):
    left_spec = load_spec_from_spec_dict(spec_dict=dict(minimal_spec_dict, definitions={'model': left_schema}))
    right_spec = load_spec_from_spec_dict(spec_dict=dict(minimal_spec_dict, definitions={'model': right_schema}))

    assert RequiredPropertiesDifferWalker(
        left_spec=left_spec,
        right_spec=right_spec,
    ).walk() == expected_diffs


def test_RequiredPropertiesDifferWalker_recursive_definition(minimal_spec_dict):

    minimal_spec_dict['definitions'] = {
        'recursive_object': {
            'type': 'object',
            'properties': {
                'property': {'$ref': '#/definitions/model'},
                'recursive_property': {'$ref': '#/definitions/recursive_object'},
            },
        },
    }
    left_spec_dict = dict(
        minimal_spec_dict,
        definitions={
            'model': {
                'properties': {
                    'old_only': {'type': 'string'},
                },
                'required': ['old_only'],
                'type': 'object',
            },
        },
    )
    right_spec_dict = dict(
        minimal_spec_dict,
        definitions={
            'model': {
                'properties': {
                    'old_only': {'type': 'string'},
                },
                'type': 'object',
            },
        },
    )
    left_spec = load_spec_from_spec_dict(spec_dict=left_spec_dict)
    right_spec = load_spec_from_spec_dict(spec_dict=right_spec_dict)

    assert RequiredPropertiesDifferWalker(
        left_spec=left_spec,
        right_spec=right_spec,
    ).walk() == [RequiredPropertiesDiff(path=('definitions', 'model'), mapping=EntityMapping(old={'old_only'}, new=set()))]
