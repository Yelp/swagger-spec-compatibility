# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy

import pytest

from swagger_spec_compatibility.rules.added_enum_value_in_response import AddedEnumValueInRequest
from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict


def test_validate_succeed(minimal_spec):
    assert list(AddedEnumValueInRequest.validate(
        left_spec=minimal_spec,
        right_spec=minimal_spec,
    )) == []


@pytest.mark.parametrize(
    'old_response_schema, new_response_schema, expected_references',
    [
        (
            {'type': 'string', 'enum': ['v1']},
            {'type': 'string', 'enum': ['v1', 'v2']},
            [''],
        ),
        (
            {
                'properties': {
                    'property_1': {
                        'properties': {
                            'inner_1': {'type': 'string', 'enum': ['v1']},
                        },
                        'type': 'object',
                    },
                },
                'type': 'object',
            },
            {
                'properties': {
                    'property_1': {'type': 'string', 'enum': ['v1', 'v2']},
                },
                'type': 'object',
            },
            ['/properties/property_1'],
        ),
        (
            {
                'properties': {
                    'common': {'type': 'string', 'enum': ['v1', 'v2', 'v3']},
                    'property_1': {
                        'type': 'object',
                        'properties': {
                            'inner': {'type': 'string', 'enum': ['v1', 'v2', 'v3']},
                        },
                    },
                },
                'type': 'object',
            },
            {
                'properties': {
                    'common': {'type': 'string', 'enum': ['v1', 'v2']},
                    'property': {
                        'type': 'object',
                        'properties': {
                            'inner': {'type': 'string', 'enum': ['v1', 'v2']},
                        },
                    },
                },
                'type': 'object',
            },
            [],
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
        AddedEnumValueInRequest.validation_message(
            reference='#/paths//endpoint/get/responses/200/schema{}'.format(reference),
        )
        for reference in expected_references
    ]
    assert list(AddedEnumValueInRequest.validate(
        left_spec=old_spec,
        right_spec=new_spec,
    )) == expected_results


@pytest.mark.parametrize(
    'schema_path, old_schema, new_schema',
    [
        [
            'definitions',
            {'model': {'type': 'string', 'enum': ['v1']}},
            {'model': {'type': 'string', 'enum': ['v1', 'v2']}},
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
                                'schema': {'type': 'string', 'enum': ['v1']},
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
                                'schema': {'type': 'string', 'enum': ['v1', 'v2']},
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

    assert list(AddedEnumValueInRequest.validate(
        left_spec=old_spec,
        right_spec=new_spec,
    )) == []
