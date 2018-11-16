# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json
import os

import mock
import pytest
import six
from bravado_core.operation import Operation  # noqa: F401
from bravado_core.spec import Spec  # noqa: F401

from swagger_spec_compatibility.cli.common import uri
from swagger_spec_compatibility.spec_utils import Endpoint
from swagger_spec_compatibility.spec_utils import get_endpoints
from swagger_spec_compatibility.spec_utils import get_operation_mappings
from swagger_spec_compatibility.spec_utils import get_operations
from swagger_spec_compatibility.spec_utils import get_required_properties
from swagger_spec_compatibility.spec_utils import HTTPVerb
from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict
from swagger_spec_compatibility.spec_utils import load_spec_from_uri
from swagger_spec_compatibility.util import EntityMapping


@pytest.fixture
def mock_operation(simple_operation_dict):
    return Operation(
        swagger_spec=mock.Mock(),
        path_name='/endpoint',
        http_method='get',
        op_spec=simple_operation_dict,
    )


def test_HTTPVerb_members_are_strings():
    assert all(isinstance(http_verb.value, six.text_type) for http_verb in HTTPVerb)


def test_HTTPVerb_from_operation(mock_operation):
    assert HTTPVerb.from_swagger_operation(mock_operation) == HTTPVerb.GET


def test_Endpoint_from_operation(mock_operation):
    assert Endpoint.from_swagger_operation(mock_operation) == Endpoint(
        http_verb=HTTPVerb.GET,
        path='/endpoint',
        operation=mock_operation,
    )


def test_Endpoint_equality_and_hash(mock_operation):
    endpoint1 = Endpoint(
        http_verb=HTTPVerb.GET,
        path='/endpoint',
        operation=mock_operation,
    )
    endpoint2 = Endpoint(
        http_verb=HTTPVerb.GET,
        path='/endpoint',
        operation=mock_operation,
    )
    endpoint3 = Endpoint(
        http_verb=HTTPVerb.POST,
        path='/endpoint',
        operation=mock_operation,
    )

    assert hash(endpoint1) == hash(endpoint2)
    assert endpoint1 == endpoint2
    assert hash(endpoint1) != hash(endpoint3)
    assert endpoint1 != endpoint3


def test_load_spec_from_uri(tmpdir, minimal_spec_dict):
    spec_path = str(os.path.join(tmpdir.strpath, 'swagger.json'))
    with open(spec_path, 'w') as f:
        json.dump(minimal_spec_dict, f)
    assert load_spec_from_uri(uri(spec_path)).spec_dict == minimal_spec_dict


def test_load_spec_from_spec(minimal_spec_dict):
    assert load_spec_from_spec_dict(minimal_spec_dict).spec_dict == minimal_spec_dict


@pytest.fixture
def spec_and_operation(minimal_spec_dict, simple_operation_dict):
    spec = load_spec_from_spec_dict(dict(
        minimal_spec_dict,
        paths={
            '/endpoint': {
                'get': simple_operation_dict,
            },
        },
    ))
    return spec, spec.resources['endpoint'].operations['get_endpoint']


def test_get_operations(minimal_spec, spec_and_operation):
    assert get_operations(minimal_spec) == []

    spec, operation = spec_and_operation
    assert get_operations(spec) == [operation]


def test_get_endpoints(minimal_spec, spec_and_operation):
    assert get_endpoints(minimal_spec) == set()

    spec, operation = spec_and_operation
    assert get_endpoints(spec) == {Endpoint.from_swagger_operation(operation)}


def test_get_operation_mappings(minimal_spec, spec_and_operation):
    assert get_operation_mappings(minimal_spec, minimal_spec) == set()

    spec, operation = spec_and_operation
    assert get_operation_mappings(spec, minimal_spec) == set()
    assert get_operation_mappings(spec, spec) == {EntityMapping(operation, operation)}


@pytest.mark.parametrize(
    'scheme, expected_result',
    [
        (None, None),
        ({}, set()),
        (
            {
                'properties': {
                    'property': {
                        'type': 'string',
                    },
                },
                'required': ['property'],
                'type': 'object',
            },
            {'property'},
        ),
    ],
)
def test_get_required_properties(minimal_spec, scheme, expected_result):
    assert get_required_properties(swagger_spec=minimal_spec, schema=scheme) == expected_result
