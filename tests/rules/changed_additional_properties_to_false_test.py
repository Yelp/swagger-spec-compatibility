# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy

import pytest

from swagger_spec_compatibility.rules.changed_additional_properties_to_false import ChangedAdditionalPropertiesToFalse
from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict


def test_validate_succeed(minimal_spec):
    assert list(
        ChangedAdditionalPropertiesToFalse.validate(
            left_spec=minimal_spec,
            right_spec=minimal_spec,
        ),
    ) == []


def test_validate_does_not_error_if_changes_in_top_level_parameters(minimal_spec_dict):
    old_spec_dict = dict(
        minimal_spec_dict,
        parameters={
            'param': {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'additionalProperties': False,
                    'properties': {
                        'property_1': {'type': 'string'},
                        'property_2': {'type': 'string'},
                    },
                    'type': 'object',
                },
            },
        },
    )
    new_spec_dict = deepcopy(old_spec_dict)
    del new_spec_dict['parameters']['param']['schema']['properties']['property_2']

    old_spec = load_spec_from_spec_dict(old_spec_dict)
    new_spec = load_spec_from_spec_dict(new_spec_dict)

    assert list(
        ChangedAdditionalPropertiesToFalse.validate(
            left_spec=old_spec,
            right_spec=new_spec,
        ),
    ) == []


@pytest.mark.parametrize(
    'old_parameter_schema, new_parameter_schema, expected_references',
    [
        (
            {
                'properties': {
                    'property_1': {'type': 'string'},
                    'property_2': {'type': 'string'},
                },
                'type': 'object',
            },
            {
                'additionalProperties': False,
                'properties': {
                    'property_1': {'type': 'string'},
                    'property_2': {'type': 'string'},
                },
                'type': 'object',
            },
            [''],
        ),
        (
            {
                'properties': {
                    'property_1': {
                        'properties': {
                            'inner_1': {'type': 'string'},
                            'inner_2': {'type': 'string'},
                        },
                        'type': 'object',
                    },
                },
                'type': 'object',
            },
            {
                'properties': {
                    'property_1': {
                        'additionalProperties': False,
                        'properties': {
                            'inner_1': {'type': 'string'},
                            'inner_2': {'type': 'string'},
                        },
                        'type': 'object',
                    },
                },
                'type': 'object',
            },
            ['/properties/property_1'],
        ),
    ],
)
def test_validate_return_an_error(
    minimal_spec_dict, simple_operation_dict, old_parameter_schema, new_parameter_schema, expected_references,
):
    old_spec_dict = dict(
        minimal_spec_dict,
        paths={
            '/endpoint': {
                'get': simple_operation_dict,
            },
        },
    )
    old_spec_dict['paths']['/endpoint']['get']['parameters'] = [{
        'in': 'body',
        'name': 'body',
        'required': True,
        'schema': old_parameter_schema,
    }]
    new_spec_dict = deepcopy(old_spec_dict)
    new_spec_dict['paths']['/endpoint']['get']['parameters'][0]['schema'] = new_parameter_schema

    old_spec = load_spec_from_spec_dict(old_spec_dict)
    new_spec = load_spec_from_spec_dict(new_spec_dict)

    expected_results = [
        ChangedAdditionalPropertiesToFalse.validation_message(
            reference='#/paths//endpoint/get/parameters/0/schema{}'.format(reference),
        )
        for reference in expected_references
    ]

    assert list(
        ChangedAdditionalPropertiesToFalse.validate(
            left_spec=old_spec,
            right_spec=new_spec,
        ),
    ) == expected_results


def test_validate_succeeds_with_changes_to_additional_properties_objects(minimal_spec_dict, simple_operation_dict):
    object_definitions = {
        'ObjectThatRefersToAnotherObject': {
            'additionalProperties': {'$ref': '#/definitions/AnotherObject'},
            'type': 'object',
        },
        'AnotherObject': {
            'type': 'object',
            'properties': {
                'property_1': {'type': 'string'}
            },
            'required': [
                'property_1',
            ]
        },
    }
    old_spec_dict = dict(
        minimal_spec_dict,
        paths={
            '/endpoint': {
                'get': simple_operation_dict,
            },
        },
        definitions=object_definitions,
    )
    old_spec_dict['paths']['/endpoint']['get']['parameters'] = [{
        'in': 'body',
        'name': 'body',
        'required': True,
        'schema': {
            'properties': {
                'property_1': {'$ref': '#/definitions/ObjectThatRefersToAnotherObject'}
            },
        },
    }]
    new_spec_dict = deepcopy(old_spec_dict)
    new_spec_dict['definitions']['AnotherObject']['properties']['property_2'] = {'type': 'string'}
    new_spec_dict['definitions']['AnotherObject']['required'].append('property_2')

    old_spec = load_spec_from_spec_dict(old_spec_dict)
    new_spec = load_spec_from_spec_dict(new_spec_dict)

    assert list(
        ChangedAdditionalPropertiesToFalse.validate(
            left_spec=old_spec,
            right_spec=new_spec,
        ),
    ) == []
