# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy

import pytest

from swagger_spec_compatibility.rules.removed_required_property_from_response import RemovedRequiredPropertyFromResponse
from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict


def test_validate_succeed(minimal_spec):
    assert list(RemovedRequiredPropertyFromResponse.validate(
        left_spec=minimal_spec,
        right_spec=minimal_spec,
    )) == []


@pytest.mark.parametrize(
    'old_response_schema, new_response_schema, expected_references',
    [
        (
            {
                'properties': {
                    'property_1': {'type': 'string'},
                },
                'required': ['property_1'],
                'type': 'object',
            },
            {
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
                        'type': 'object',
                        'properties': {
                            'inner_1': {'type': 'string'},
                        },
                        'required': ['inner_1'],
                    },
                },
                'type': 'object',
            },
            {
                'properties': {
                    'property_1': {'type': 'string'},
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
                            'inner_1': {'type': 'string'},
                        },
                        'required': ['inner_1'],
                    },
                },
                'required': ['common'],
                'type': 'object',
            },
            {
                'properties': {
                    'common': {'type': 'string'},
                    'property_1': {
                        'type': 'object',
                        'properties': {
                            'inner_1': {'type': 'string'},
                            'inner_new': {'type': 'string'},
                        },
                        'required': ['inner_1', 'inner_new'],
                    },
                },
                'required': ['common'],
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
        RemovedRequiredPropertyFromResponse.validation_message(
            reference='#/paths//endpoint/get/responses/200/schema{}'.format(reference),
        )
        for reference in expected_references
    ]
    assert list(RemovedRequiredPropertyFromResponse.validate(
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
                    'properties': {
                        'only_old': {'type': 'string'},
                    },
                    'required': ['only_old'],
                },
            },
            {
                'model': {
                    'type': 'object',
                    'properties': {
                        'only_old': {'type': 'string'},
                    },
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
                                    'properties': {
                                        'only_old': {'type': 'string'},
                                    },
                                    'required': ['only_old'],
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
                                    'properties': {
                                        'only_old': {'type': 'string'},
                                    },
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
    # FIXME: note the second case does not get identified at all :(
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

    assert list(RemovedRequiredPropertyFromResponse.validate(
        left_spec=old_spec,
        right_spec=new_spec,
    )) == []
