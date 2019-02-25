# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy

import pytest

from swagger_spec_compatibility.rules.added_properties_in_response_objects_with_additional_properties_set_to_false import AddedPropertiesInResponseObjectsWithAdditionalPropertiesSetToFalse  # noqa
from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict


def test_validate_succeed(minimal_spec):
    assert list(AddedPropertiesInResponseObjectsWithAdditionalPropertiesSetToFalse.validate(
        left_spec=minimal_spec,
        right_spec=minimal_spec,
    )) == []


@pytest.mark.parametrize(
    'old_response_schema, new_response_schema, expected_references',
    [
        (
            {
                'additionalProperties': False,
                'properties': {
                    'property_1': {'type': 'string'},
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
                        'additionalProperties': False,
                        'properties': {
                            'inner_1': {'type': 'string'},
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
        (
            {
                'properties': {
                    'common': {'type': 'object'},
                    'property_1': {
                        'type': 'object',
                        'properties': {
                            'inner_1': {
                                'additionalProperties': False,
                                'properties': {
                                    'property_1': {'type': 'string'},
                                    'property_2': {'type': 'string'},
                                },
                                'type': 'object',
                            },
                        },
                    },
                },
                'type': 'object',
            },
            {
                'properties': {
                    'common': {'type': 'string'},
                    'property_1': {
                        'type': 'object',
                        'properties': {
                            'inner_1': {
                                'additionalProperties': False,
                                'properties': {
                                    'property_1': {'type': 'string'},
                                },
                                'type': 'object',
                            },
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
        AddedPropertiesInResponseObjectsWithAdditionalPropertiesSetToFalse.validation_message(
            reference='#/paths//endpoint/get/responses/200/schema{}'.format(reference),
        )
        for reference in expected_references
    ]
    assert list(AddedPropertiesInResponseObjectsWithAdditionalPropertiesSetToFalse.validate(
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
                    'additionalProperties': False,
                    'properties': {
                        'property_1': {'type': 'string'},
                    },
                    'type': 'object',
                },
            },
            {
                'model': {
                    'additionalProperties': False,
                    'properties': {
                        'property_1': {'type': 'string'},
                        'property_2': {'type': 'string'},
                    },
                    'type': 'object',
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
                                    'additionalProperties': False,
                                    'properties': {
                                        'property_1': {'type': 'string'},
                                    },
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
                                    'additionalProperties': False,
                                    'properties': {
                                        'property_1': {'type': 'string'},
                                        'property_2': {'type': 'string'},
                                    },
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

    assert list(AddedPropertiesInResponseObjectsWithAdditionalPropertiesSetToFalse.validate(
        left_spec=old_spec,
        right_spec=new_spec,
    )) == []


def test_validate_does_not_error_if_changes_to_additional_properties_type(minimal_spec_dict, simple_operation_dict):
    old_spec_dict = dict(
        minimal_spec_dict,
        paths={
            '/endpoint': {
                'get': simple_operation_dict,
            },
        },
    )
    old_spec_dict['paths']['/endpoint']['get']['responses']['200']['schema'] = {
        'additionalProperties': False,
        'properties': {
            'property_1': {'type': 'string'},
            'property_2': {'type': 'string'},
        },
        'type': 'object',
    }
    new_spec_dict = deepcopy(old_spec_dict)
    del new_spec_dict['paths']['/endpoint']['get']['responses']['200']['schema']['additionalProperties']

    old_spec = load_spec_from_spec_dict(old_spec_dict)
    new_spec = load_spec_from_spec_dict(new_spec_dict)

    assert list(AddedPropertiesInResponseObjectsWithAdditionalPropertiesSetToFalse.validate(
        left_spec=old_spec,
        right_spec=new_spec,
    )) == []
