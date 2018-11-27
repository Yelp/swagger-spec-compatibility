# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest
from bravado_core.spec import Spec

from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict
from swagger_spec_compatibility.util import EntityMapping
from swagger_spec_compatibility.walkers.changed_types import _different_types_mapping
from swagger_spec_compatibility.walkers.changed_types import ChangedTypesDiff
from swagger_spec_compatibility.walkers.changed_types import ChangedTypesDifferWalker


@pytest.mark.parametrize(
    'default_type_to_object, left_schema, right_schema, expected_value',
    [
        (False, None, None, None),
        (True, None, None, None),
        (False, {}, {}, None),
        (True, {}, {}, None),
        (False, {'type': 'object'}, {}, EntityMapping(old='object', new=None)),
        (True, {'type': 'object'}, {}, None),
        (False, {'type': 'object'}, {'type': 'string'}, EntityMapping(old='object', new='string')),
        (True, {'type': 'object'}, {'type': 'string'}, EntityMapping(old='object', new='string')),
    ],
)
def test__different_types_mapping(
    default_type_to_object, left_schema, right_schema, expected_value,
):
    assert _different_types_mapping(
        left_spec=mock.Mock(
            spec=Spec,
            config={'default_type_to_object': default_type_to_object},
        ),
        right_spec=mock.Mock(
            spec=Spec,
            config={'default_type_to_object': default_type_to_object},
        ),
        left_schema=left_schema,
        right_schema=right_schema,
    ) == expected_value


@pytest.mark.parametrize(
    'left_schema, right_schema, expected_diffs',
    [
        ({}, {}, []),
        (
            {'type': 'object'},
            {'type': 'object'},
            [],
        ),
        (
            {'type': 'object'},
            {},
            [ChangedTypesDiff(path=('definitions', 'model'), mapping=EntityMapping(old='object', new=None))],
        ),
        (
            {'type': 'object'},
            {'type': 'string'},
            [ChangedTypesDiff(path=('definitions', 'model'), mapping=EntityMapping(old='object', new='string'))],
        ),
        (
            {
                'type': 'object',
                'properties': {
                    'property': {'type': 'object'},
                },
            },
            {
                'type': 'object',
                'properties': {
                    'property': {'type': 'object'},
                },
            },
            [],
        ),
        (
            {
                'type': 'object',
                'properties': {
                    'property': {'type': 'object'},
                },
            },
            {
                'type': 'object',
                'properties': {
                    'property': {'type': 'string'},
                },
            },
            [
                ChangedTypesDiff(
                    path=('definitions', 'model', 'properties', 'property'),
                    mapping=EntityMapping(old='object', new='string'),
                ),
            ],
        ),
    ],
)
def test_ChangedTypesDifferWalker(minimal_spec_dict, left_schema, right_schema, expected_diffs):
    left_spec = load_spec_from_spec_dict(spec_dict=dict(minimal_spec_dict, definitions={'model': left_schema}))
    right_spec = load_spec_from_spec_dict(spec_dict=dict(minimal_spec_dict, definitions={'model': right_schema}))

    assert ChangedTypesDifferWalker(
        left_spec=left_spec,
        right_spec=right_spec,
    ).walk() == expected_diffs
