# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict
from swagger_spec_compatibility.util import EntityMapping
from swagger_spec_compatibility.walkers.changed_xnullable import ChangedXNullableDiff
from swagger_spec_compatibility.walkers.changed_xnullable import ChangedXNullableDifferWalker


@pytest.mark.parametrize(
    'left_schema, right_schema, expected_diffs',
    [
        ({}, {}, []),
        (
            {'type': 'object', 'x-nullable': False},
            {'type': 'object'},
            [],
        ),
        (
            {'type': 'object'},
            {'type': 'object', 'x-nullable': False},
            [],
        ),
        (
            {'type': 'object', 'x-nullable': True},
            {'type': 'object'},
            [ChangedXNullableDiff(path=('definitions', 'model', 'x-nullable'), mapping=EntityMapping(old=True, new=False))],
        ),
        (
            {'type': 'object'},
            {'type': 'object', 'x-nullable': True},
            [ChangedXNullableDiff(path=('definitions', 'model', 'x-nullable'), mapping=EntityMapping(old=False, new=True))],
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
                    'property': {'type': 'object', 'x-nullable': True},
                },
            },
            [
                ChangedXNullableDiff(
                    path=('definitions', 'model', 'properties', 'property', 'x-nullable'),
                    mapping=EntityMapping(old=False, new=True),
                ),
            ],
        ),
    ],
)
def test_ChangedXNullableDifferWalker(minimal_spec_dict, left_schema, right_schema, expected_diffs):
    left_spec = load_spec_from_spec_dict(spec_dict=dict(minimal_spec_dict, definitions={'model': left_schema}))
    right_spec = load_spec_from_spec_dict(spec_dict=dict(minimal_spec_dict, definitions={'model': right_schema}))

    assert ChangedXNullableDifferWalker(
        left_spec=left_spec,
        right_spec=right_spec,
    ).walk() == expected_diffs
