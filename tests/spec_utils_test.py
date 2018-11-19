# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json
import os
import typing  # noqa: F401

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
from swagger_spec_compatibility.spec_utils import iterate_on_responses_status_codes
from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict
from swagger_spec_compatibility.spec_utils import load_spec_from_uri
from swagger_spec_compatibility.spec_utils import SchemaWalker
from swagger_spec_compatibility.spec_utils import StatusCodeSchema
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


@pytest.mark.parametrize(
    'old_operation_dict, new_operation_dict, expected_result',
    [
        [
            {'responses': {'200': {'schema': {}}}},
            {'responses': {'200': {'schema': {}}}},
            [StatusCodeSchema('200', EntityMapping({}, {}))],
        ],
        [
            {'responses': {'200': {'schema': {}}, '300': {'schema': {}}}},
            {'responses': {'200': {'schema': {}}}},
            [StatusCodeSchema('200', EntityMapping({}, {}))],
        ],
        [
            {'responses': {'200': {'schema': {}}, '300': {'schema': {'type': 'integer'}}}},
            {'responses': {'200': {'schema': {}}, '300': {'schema': {'type': 'string'}}}},
            [
                StatusCodeSchema('200', EntityMapping({}, {})),
                StatusCodeSchema('300', EntityMapping({'type': 'integer'}, {'type': 'string'})),
            ],
        ],
        [
            {'responses': {'200': {}}},
            {'responses': {'300': {}}},
            [],
        ],
    ],
)
def test_iterate_on_responses_status_codes(old_operation_dict, new_operation_dict, expected_result):
    result = list(iterate_on_responses_status_codes(old_operation_dict, new_operation_dict))
    if not expected_result:
        assert not result
    else:
        expected_result = sorted(expected_result)
        assert sorted(result) == expected_result


def test_SchemaWalker_pass_through_all_the_items():
    spec = mock.Mock(
        spec=Spec,
        deref_flattened_spec={
            'dict': {
                'dict_dict': {},
                'dict_list': [],
                'dict_value': None,
            },
            'list': [
                {},
                [],
                None,
            ],
            'value': None,
        },
    )

    class DummySchemaWalker(SchemaWalker):
        left_spec = None  # type: Spec
        right_spec = None  # type: Spec
        additional = None  # type: bool

        recorded_calls = {
            'dict_check_paths': set(),
            'list_check_paths': set(),
            'value_check_paths': set(),
        }  # type: typing.MutableMapping[typing.Text, typing.Set[typing.Tuple[typing.Text, ...]]]

        def dict_check(self, path, old_dict, new_dict):
            self.recorded_calls['dict_check_paths'].add(path)

        def list_check(self, path, old_list, new_list):
            self.recorded_calls['list_check_paths'].add(path)

        def value_check(self, path, old_value, new_value):
            self.recorded_calls['value_check_paths'].add(path)

        def walk_response(self):
            return self.recorded_calls

    walker = DummySchemaWalker(spec, spec, additional=True)
    assert walker.left_spec == spec
    assert walker.right_spec == spec
    assert walker.additional is True
    assert walker.walk() == {
        'dict_check_paths': {
            tuple(),
            ('dict',),
            ('dict', 'dict_dict',),
        },
        'list_check_paths': {
            ('dict', 'dict_list',),
            ('list',),
            ('list', '1',),
        },
        'value_check_paths': {
            ('dict', 'dict_value',),
            ('value',),
            ('list', '0',),
            ('list', '1', '0',),
            ('list', '1', '1',),
            ('list', '1', '2',),
            ('list', '2',),
        },
    }
