# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict
from swagger_spec_compatibility.util import EntityMapping
from swagger_spec_compatibility.walkers.additional_properties import _evaluate_additional_properties_diffs
from swagger_spec_compatibility.walkers.additional_properties import AdditionalPropertiesDiff
from swagger_spec_compatibility.walkers.additional_properties import AdditionalPropertiesDifferWalker
from swagger_spec_compatibility.walkers.additional_properties import DiffType


@pytest.mark.parametrize(
    'left_dict, right_dict, expected_value',
    [
        (None, None, []),
        ({}, {}, []),
        (
            {'additionalProperties': True},
            {},
            [],
        ),
        (
            {'additionalProperties': True},
            {'additionalProperties': {}},
            [],
        ),
        (
            {'additionalProperties': True},
            {'additionalProperties': False},
            [
                AdditionalPropertiesDiff(
                    path=mock.sentinel.PATH,
                    diff_type=DiffType.VALUE,
                    additionalProperties=EntityMapping(old=True, new=False),
                    properties=None,
                ),
            ],
        ),
        (
            {'additionalProperties': {}},
            {'additionalProperties': False},
            [
                AdditionalPropertiesDiff(
                    path=mock.sentinel.PATH,
                    diff_type=DiffType.VALUE,
                    additionalProperties=EntityMapping(old=True, new=False),
                    properties=None,
                ),
            ],
        ),
        (
            {'additionalProperties': True},
            {'additionalProperties': {'type': 'string'}},
            [
                AdditionalPropertiesDiff(
                    path=mock.sentinel.PATH,
                    diff_type=DiffType.VALUE,
                    additionalProperties=EntityMapping(old=True, new={'type': 'string'}),
                    properties=None,
                ),
            ],
        ),
        (
            {'additionalProperties': False},
            {},
            [
                AdditionalPropertiesDiff(
                    path=mock.sentinel.PATH,
                    diff_type=DiffType.VALUE,
                    additionalProperties=EntityMapping(old=False, new=True),
                    properties=None,
                ),
            ],
        ),
        (
            {'additionalProperties': False},
            {'additionalProperties': {}},
            [
                AdditionalPropertiesDiff(
                    path=mock.sentinel.PATH,
                    diff_type=DiffType.VALUE,
                    additionalProperties=EntityMapping(old=False, new=True),
                    properties=None,
                ),
            ],
        ),
        (
            {'additionalProperties': True},
            {'additionalProperties': False},
            [
                AdditionalPropertiesDiff(
                    path=mock.sentinel.PATH,
                    diff_type=DiffType.VALUE,
                    additionalProperties=EntityMapping(old=True, new=False),
                    properties=None,
                ),
            ],
        ),
        (
            {
                'additionalProperties': True,
                'properties': {
                    'property_1': {'type': 'object'},
                },
            },
            {
                'additionalProperties': True,
                'properties': {
                    'property_1': {'type': 'object'},
                    'property_2': {'type': 'object'},
                },
            },
            [],
        ),
        (
            {
                'additionalProperties': False,
                'properties': {
                    'property_1': {'type': 'object'},
                },
                'type': 'object',
            },
            {
                'additionalProperties': False,
                'properties': {
                    'property_1': {'type': 'object'},
                    'property_2': {'type': 'object'},
                },
                'type': 'object',
            },
            [
                AdditionalPropertiesDiff(
                    path=mock.sentinel.PATH,
                    diff_type=DiffType.PROPERTIES,
                    additionalProperties=None,
                    properties=EntityMapping(old=set(), new={'property_2'}),
                ),
            ],
        ),
        (
            {
                'additionalProperties': True,
                'properties': {
                    'property_1': {'type': 'object'},
                },
                'type': 'object',
            },
            {
                'additionalProperties': False,
                'properties': {
                    'property_1': {'type': 'object'},
                    'property_2': {'type': 'object'},
                },
                'type': 'object',
            },
            [
                AdditionalPropertiesDiff(
                    path=mock.sentinel.PATH,
                    diff_type=DiffType.VALUE,
                    additionalProperties=EntityMapping(old=True, new=False),
                    properties=None,
                ),
                AdditionalPropertiesDiff(
                    path=mock.sentinel.PATH,
                    diff_type=DiffType.PROPERTIES,
                    additionalProperties=None,
                    properties=EntityMapping(old=set(), new={'property_2'}),
                ),
            ],
        ),
    ],
)
@mock.patch('swagger_spec_compatibility.walkers.additional_properties.get_properties', autospec=True)
def test__evaluate_additional_properties_diffs(mock_get_properties, left_dict, right_dict, expected_value):
    mock_get_properties.side_effect = [
        set(left_dict.get('properties', {})) if left_dict else None,
        set(right_dict.get('properties', {})) if right_dict else None,
    ]

    assert _evaluate_additional_properties_diffs(
        path=mock.sentinel.PATH,
        left_spec=mock.sentinel.LEFT_SPEC,
        right_spec=mock.sentinel.RIGHT_SPEC,
        left_schema=left_dict,
        right_schema=right_dict,
    ) == expected_value


@pytest.mark.parametrize(
    'left_schema, right_schema, expected_diffs',
    [
        ({}, {}, []),
        (
            {'type': 'object'},
            {'additionalProperties': False, 'type': 'object'},
            [
                AdditionalPropertiesDiff(
                    path=('definitions', 'model'),
                    diff_type=DiffType.VALUE,
                    additionalProperties=EntityMapping(old=True, new=False),
                    properties=None,
                ),
            ],
        ),
        (
            {
                'type': 'object',
            },
            {'additionalProperties': False, 'type': 'object'},
            [
                AdditionalPropertiesDiff(
                    path=('definitions', 'model'),
                    diff_type=DiffType.VALUE,
                    additionalProperties=EntityMapping(old=True, new=False),
                    properties=None,
                ),
            ],
        ),
    ],
)
def test_AdditionalPropertiesDifferWalker(minimal_spec_dict, left_schema, right_schema, expected_diffs):
    left_spec = load_spec_from_spec_dict(spec_dict=dict(minimal_spec_dict, definitions={'model': left_schema}))
    right_spec = load_spec_from_spec_dict(spec_dict=dict(minimal_spec_dict, definitions={'model': right_schema}))

    assert AdditionalPropertiesDifferWalker(
        left_spec=left_spec,
        right_spec=right_spec,
    ).walk() == expected_diffs
