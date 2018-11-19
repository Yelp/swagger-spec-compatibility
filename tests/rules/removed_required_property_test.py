# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy

import pytest

from swagger_spec_compatibility.rules.removed_required_property import RemovedRequiredProperty
from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict


def test_validate_succeed(minimal_spec):
    assert list(RemovedRequiredProperty.validate(
        left_spec=minimal_spec,
        right_spec=minimal_spec,
    )) == []


@pytest.mark.parametrize(
    'old_response_schema, new_response_schema, expected_references',
    [
        (
            {
                'properties': {
                    'property_1': {
                        'type': 'string',
                    },
                },
                'required': [
                    'property_1',
                ],
                'type': 'object',
            },
            {
                'properties': {
                    'property_1': {
                        'type': 'string',
                    },
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
                            'inner_1': {
                                'type': 'string',
                            },
                        },
                        'required': [
                            'inner_1',
                        ],
                    },
                },
                'type': 'object',
            },
            {
                'properties': {
                    'property_1': {
                        'type': 'string',
                    },
                },
                'type': 'object',
            },
            ['/properties/property_1'],
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
        RemovedRequiredProperty.validation_message(
            reference='#/paths//endpoint/get/responses/200/schema{}'.format(reference),
        )
        for reference in expected_references
    ]
    a = list(RemovedRequiredProperty.validate(
        left_spec=old_spec,
        right_spec=new_spec,
    ))
    print(a)
    print(expected_results)
    assert a == expected_results
