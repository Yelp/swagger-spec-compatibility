# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy

import pytest

from swagger_spec_compatibility.rules.changed_type import ChangedType
from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict


@pytest.mark.parametrize(
    'schema_path, old_schema, new_schema',
    [
        (
            # Equivalent specs does not have errors to be reported
            'definitions',
            {},
            {},
        ),
        (
            # Changes in object schema not used as request parameter or response body are not reported
            'definitions',
            {'model': {'type': 'string'}},
            {'model': {'type': 'object'}},
        ),
        (
            # Changes in object schema not used as request parameter or response body are not reported
            'parameters',
            {
                'model': {
                    'in': 'body',
                    'name': 'body',
                    'required': True,
                    'schema': {'type': 'string'},
                },
            },
            {
                'model': {
                    'in': 'body',
                    'name': 'body',
                    'required': True,
                    'schema': {'type': 'object'},
                },
            },
        ),
        (
            # Changes in object schema not used as request parameter or response body are not reported
            'responses',
            {'model': {'description': '', 'schema': {'type': 'string'}}},
            {'model': {'description': '', 'schema': {'type': 'object'}}},
        ),
    ],
)
def test_validate_succeed(
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

    assert list(
        ChangedType.validate(
            left_spec=old_spec,
            right_spec=new_spec,
        ),
    ) == []


@pytest.mark.parametrize(
    'is_parameter, old_schema, new_schema, expected_references',
    [
        (
            True,
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {'type': 'string'},
            },
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {'type': 'object'},
            },
            ['/parameters/0/schema'],
        ),
        (
            True,
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'properties': {
                        'property': {'type': 'string'},
                    },
                    'type': 'object',
                },
            },
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'properties': {
                        'property': {'type': 'object'},
                    },
                    'type': 'object',
                },
            },
            ['/parameters/0/schema/properties/property'],
        ),
        (
            False,
            {'type': 'string'},
            {'type': 'object'},
            ['/responses/200/schema'],
        ),
        (
            False,
            {
                'properties': {
                    'property': {'type': 'string'},
                },
                'type': 'object',
            },
            {
                'properties': {
                    'property': {'type': 'object'},
                },
                'type': 'object',
            },
            ['/responses/200/schema/properties/property'],
        ),
    ],
)
def test_validate_return_an_error(
    minimal_spec_dict, simple_operation_dict, is_parameter, old_schema, new_schema, expected_references,
):
    base_spec = dict(
        minimal_spec_dict,
        paths={
            '/endpoint': {
                'get': simple_operation_dict,
            },
        },
    )
    old_spec_dict = deepcopy(base_spec)
    new_spec_dict = deepcopy(base_spec)

    if is_parameter:
        old_spec_dict['paths']['/endpoint']['get']['parameters'] = [old_schema]
        new_spec_dict['paths']['/endpoint']['get']['parameters'] = [new_schema]
    else:
        old_spec_dict['paths']['/endpoint']['get']['responses']['200']['schema'] = old_schema
        new_spec_dict['paths']['/endpoint']['get']['responses']['200']['schema'] = new_schema

    old_spec = load_spec_from_spec_dict(old_spec_dict)
    new_spec = load_spec_from_spec_dict(new_spec_dict)

    expected_results = [
        ChangedType.validation_message(
            reference='#/paths//endpoint/get{}'.format(reference),
        )
        for reference in expected_references
    ]

    assert list(
        ChangedType.validate(
            left_spec=old_spec,
            right_spec=new_spec,
        ),
    ) == expected_results
