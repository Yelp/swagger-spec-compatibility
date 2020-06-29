# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy

import pytest

from swagger_spec_compatibility.rules.removed_properties_from_request_objects_with_additional_properties_set_to_false import RemovedPropertiesFromRequestObjectsWithAdditionalPropertiesSetToFalse  # noqa
from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict


def test_validate_succeed(minimal_spec):
    assert list(
        RemovedPropertiesFromRequestObjectsWithAdditionalPropertiesSetToFalse.validate(
            left_spec=minimal_spec,
            right_spec=minimal_spec,
        ),
    ) == []


def test_validate_succeed_if_parameters_are_defined_in_different_locations(minimal_spec_dict, simple_operation_dict):
    parameter_schema = {
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
    }
    old_spec = load_spec_from_spec_dict(
        dict(
            minimal_spec_dict,
            paths={
                '/endpoint': {
                    'parameters': [parameter_schema],
                    'get': simple_operation_dict,
                },
            },
        ),
    )
    new_spec = load_spec_from_spec_dict(
        dict(
            minimal_spec_dict,
            paths={
                '/endpoint': {
                    'get': dict(
                        simple_operation_dict,
                        parameters=[parameter_schema],
                    ),
                },
            },
        ),
    )

    assert list(
        RemovedPropertiesFromRequestObjectsWithAdditionalPropertiesSetToFalse.validate(
            left_spec=old_spec,
            right_spec=new_spec,
        ),
    ) == []


@pytest.mark.parametrize(
    'old_parameter_schema, new_parameter_schema, expected_references',
    [
        (
            {
                'additionalProperties': False,
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
            [],
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
        RemovedPropertiesFromRequestObjectsWithAdditionalPropertiesSetToFalse.validation_message(
            reference='#/paths//endpoint/get/parameters/0/schema{}'.format(reference),
        )
        for reference in expected_references
    ]
    assert list(
        RemovedPropertiesFromRequestObjectsWithAdditionalPropertiesSetToFalse.validate(
            left_spec=old_spec,
            right_spec=new_spec,
        ),
    ) == expected_results


def test_validate_does_not_error_if_changes_in_response_schema(minimal_spec_dict):
    old_spec_dict = dict(
        minimal_spec_dict,
        paths={
            '/endpoint': {
                'get': {
                    'responses': {
                        '200': {
                            'description': '',
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
                },
            },
        },
    )
    new_spec_dict = deepcopy(old_spec_dict)
    del new_spec_dict['paths']['/endpoint']['get']['responses']['200']['schema']['properties']['property_2']

    old_spec = load_spec_from_spec_dict(old_spec_dict)
    new_spec = load_spec_from_spec_dict(new_spec_dict)

    assert list(
        RemovedPropertiesFromRequestObjectsWithAdditionalPropertiesSetToFalse.validate(
            left_spec=old_spec,
            right_spec=new_spec,
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
        RemovedPropertiesFromRequestObjectsWithAdditionalPropertiesSetToFalse.validate(
            left_spec=old_spec,
            right_spec=new_spec,
        ),
    ) == []


def test_validate_does_not_error_if_changes_to_additional_properties_type(minimal_spec_dict, simple_operation_dict):
    old_spec_dict = dict(
        minimal_spec_dict,
        paths={
            '/endpoint': {
                'get': dict(
                    simple_operation_dict,
                    parameters=[{
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
                    }],
                ),
            },
        },
    )
    new_spec_dict = deepcopy(old_spec_dict)
    del new_spec_dict['paths']['/endpoint']['get']['parameters'][0]['schema']['additionalProperties']

    old_spec = load_spec_from_spec_dict(old_spec_dict)
    new_spec = load_spec_from_spec_dict(new_spec_dict)

    assert list(
        RemovedPropertiesFromRequestObjectsWithAdditionalPropertiesSetToFalse.validate(
            left_spec=old_spec,
            right_spec=new_spec,
        ),
    ) == []


# FIXME ensure that the feature is complete and not best guess only
@pytest.mark.xfail(reason='This is a known issue, at the moment we do not associate parameters defined in different locations')
def test_validate_fails_if_parameters_are_defined_in_different_locations_with_different_required_properties(
    minimal_spec_dict, simple_operation_dict,
):
    parameter_schema = {
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
    }
    old_spec = load_spec_from_spec_dict(
        dict(
            minimal_spec_dict,
            paths={
                '/endpoint': {
                    'parameters': [deepcopy(parameter_schema)],
                    'get': simple_operation_dict,
                },
            },
        ),
    )
    new_spec_dict = dict(
        minimal_spec_dict,
        paths={
            '/endpoint': {
                'get': dict(
                    simple_operation_dict,
                    parameters=[deepcopy(parameter_schema)],
                ),
            },
        },
    )
    del new_spec_dict['paths']['/endpoint']['get']['parameters'][0]['schema']['properties']['property_2']
    new_spec = load_spec_from_spec_dict(new_spec_dict)

    assert list(
        RemovedPropertiesFromRequestObjectsWithAdditionalPropertiesSetToFalse.validate(
            left_spec=old_spec,
            right_spec=new_spec,
        ),
    ) == [
        RemovedPropertiesFromRequestObjectsWithAdditionalPropertiesSetToFalse.validation_message(
            reference='#/paths//endpoint/get/parameters/0/schema',
        ),
    ]
