# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy

import pytest

from swagger_spec_compatibility.rules.added_nullable_property_in_response import AddedNullablePropertyInResponse
from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict


def test_validate_succeed(minimal_spec):
    assert list(AddedNullablePropertyInResponse.validate(
        left_spec=minimal_spec,
        right_spec=minimal_spec,
    )) == []


@pytest.mark.parametrize(
    'old_response_schema, new_response_schema, expected_references',
    [
        (
            {'type': 'object'},
            {'type': 'object'},
            [],
        ),
        (
            {'type': 'object', 'x-nullable': True},
            {'type': 'object'},
            [],
        ),
        (
            {'type': 'object', 'x-nullable': False},
            {'type': 'object'},
            [],
        ),
        (
            {'type': 'object'},
            {'type': 'object', 'x-nullable': True},
            ['/x-nullable'],
        ),
        (
            {
                'properties': {
                    'property_1': {'type': 'string'},
                },
                'type': 'object',
            },
            {
                'properties': {
                    'property_1': {'type': 'string'},
                },
                'type': 'object',
            },
            [],
        ),
        (
            {
                'properties': {
                    'property_1': {'type': 'string', 'x-nullable': True},
                },
                'type': 'object',
            },
            {
                'properties': {
                    'property_1': {'type': 'string'},
                },
                'type': 'object',
            },
            [],
        ),
        (
            {
                'properties': {
                    'property_1': {'type': 'string'},
                },
                'type': 'object',
            },
            {
                'properties': {
                    'property_1': {'type': 'string', 'x-nullable': False},
                },
                'type': 'object',
            },
            [],
        ),
        (
            {
                'properties': {
                    'property_1': {'type': 'string'},
                },
                'type': 'object',
            },
            {
                'properties': {
                    'property_1': {'type': 'string', 'x-nullable': True},
                },
                'type': 'object',
            },
            ['/properties/property_1/x-nullable'],
        ),
    ],
)
def test_validate_return_an_error(
    minimal_spec_dict, simple_operation_dict, old_response_schema, new_response_schema, expected_references,
):
    old_spec_dict = dict(
        minimal_spec_dict,
        paths={
            '/endpoint': {
                'get': simple_operation_dict,
            },
        },
    )
    old_spec_dict['paths']['/endpoint']['get']['responses']['200']['schema'] = old_response_schema
    new_spec_dict = deepcopy(old_spec_dict)
    new_spec_dict['paths']['/endpoint']['get']['responses']['200']['schema'] = new_response_schema

    old_spec = load_spec_from_spec_dict(old_spec_dict)
    new_spec = load_spec_from_spec_dict(new_spec_dict)

    expected_results = [
        AddedNullablePropertyInResponse.validation_message(
            reference='#/paths//endpoint/get/responses/200/schema{}'.format(reference),
        )
        for reference in expected_references
    ]
    assert list(AddedNullablePropertyInResponse.validate(
        left_spec=old_spec,
        right_spec=new_spec,
    )) == expected_results


@pytest.mark.parametrize(
    'schema_path, old_schema, new_schema',
    [
        [
            'definitions',
            {
                'model': {
                    'type': 'object',
                },
            },
            {
                'model': {
                    'type': 'object',
                    'x-models': True,
                },
            },
        ],
        [
            'paths',
            {
                '/endpoint': {
                    'get': {
                        'parameters': [
                            {
                                'name': 'body',
                                'in': 'body',
                                'required': True,
                                'schema': {
                                    'type': 'object',
                                },
                            },
                        ],
                        'responses': {
                            '200': {'description': ''},
                        },
                    },
                },
            },
            {
                '/endpoint': {
                    'get': {
                        'parameters': [
                            {
                                'name': 'body',
                                'in': 'body',
                                'required': True,
                                'schema': {
                                    'type': 'object',
                                    'x-nullable': True,
                                },
                            },
                        ],
                        'responses': {
                            '200': {'description': ''},
                        },
                    },
                },
            },
        ],
    ],
)
def test_validate_does_not_errors_if_changes_in_parameters_or_definitions(
    minimal_spec_dict, simple_operation_dict, schema_path, old_schema, new_schema,
):
    base_spec = dict(
        minimal_spec_dict,
        paths={
            '/endpoint': {
                'get': simple_operation_dict,
            },
        },
    )

    old_spec_dict = dict(
        base_spec,
        **{
            schema_path: old_schema,
        }
    )
    new_spec_dict = dict(
        base_spec,
        **{
            schema_path: new_schema,
        }
    )

    old_spec = load_spec_from_spec_dict(old_spec_dict)
    new_spec = load_spec_from_spec_dict(new_spec_dict)

    assert list(AddedNullablePropertyInResponse.validate(
        left_spec=old_spec,
        right_spec=new_spec,
    )) == []
