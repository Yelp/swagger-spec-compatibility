# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing
from enum import Enum
from itertools import chain

from bravado.client import SwaggerClient
from bravado_core.operation import Operation  # noqa: F401
from bravado_core.spec import Spec  # noqa: F401
from bravado_core.util import determine_object_type
from bravado_core.util import ObjectType
from six import iterkeys
from swagger_spec_validator.validator20 import get_collapsed_properties_type_mappings

from swagger_spec_compatibility.cache import typed_lru_cache
from swagger_spec_compatibility.util import EntityMapping


class HTTPVerb(Enum):
    DELETE = 'delete'
    GET = 'get'
    HEAD = 'head'
    OPTIONS = 'options'
    PARAMETERS = 'parameters'
    PATCH = 'patch'
    POST = 'post'
    PUT = 'put'

    @staticmethod
    def from_swagger_operation(operation):
        # type: (Operation) -> 'HTTPVerb'
        return HTTPVerb(operation.http_method)


class Endpoint(typing.NamedTuple(
    '_Endpoint', (
        ('http_verb', HTTPVerb),
        ('path', typing.Text),
        ('operation', Operation),
    ),
)):

    @staticmethod
    def from_swagger_operation(operation):
        # type: (Operation) -> 'Endpoint'
        return Endpoint(
            http_verb=HTTPVerb.from_swagger_operation(operation),
            path=operation.path_name,
            operation=operation,
        )

    def __hash__(self):
        # type: () -> int
        return hash((hash(self.http_verb), hash(self.path)))

    def __eq__(self, other):
        # type: (typing.Any) -> bool
        return isinstance(other, self.__class__) and self.http_verb == other.http_verb and self.path == other.path


@typed_lru_cache(maxsize=2)
def load_spec_from_uri(uri):
    # type: (typing.Text) -> Spec
    return SwaggerClient.from_url(uri, config={'internally_dereference_refs': True}).swagger_spec


def load_spec_from_spec_dict(spec_dict):
    # type: (typing.Mapping[typing.Text, typing.Any]) -> Spec
    return SwaggerClient.from_spec(spec_dict, origin_url='', config={'internally_dereference_refs': True}).swagger_spec


@typed_lru_cache(maxsize=2)
def get_operations(spec):
    # type: (Spec) -> typing.List[Operation]
    return [
        operation
        for resource in spec.resources.values()
        for operation in resource.operations.values()
    ]


@typed_lru_cache(maxsize=2)
def get_endpoints(spec):
    # type: (Spec) -> typing.Set[Endpoint]
    return {
        Endpoint.from_swagger_operation(operation)
        for operation in get_operations(spec)
    }


def get_operation_mappings(old_spec, new_spec):
    # type: (Spec, Spec) -> typing.Set[EntityMapping[Operation]]
    old_endpoints = get_endpoints(old_spec)
    old_endpoints_map = {  # Small hack to make endpoint search easy
        endpoint: endpoint
        for endpoint in old_endpoints
    }
    new_endpoints = get_endpoints(new_spec)
    new_endpoints_map = {  # Small hack to make endpoint search easy
        endpoint: endpoint
        for endpoint in new_endpoints
    }

    return {
        EntityMapping(old_endpoints_map[endpoint].operation, new_endpoints_map[endpoint].operation)
        for endpoint in old_endpoints.intersection(new_endpoints)
    }


def get_required_properties(swagger_spec, schema):
    # type: (Spec, typing.Optional[typing.Mapping[typing.Text, typing.Any]]) -> typing.Optional[typing.Set[typing.Text]]
    if schema is None or determine_object_type(schema) != ObjectType.SCHEMA:
        return None
    required, _ = get_collapsed_properties_type_mappings(definition=schema, deref=swagger_spec.deref)
    return set(iterkeys(required))


def get_properties(swagger_spec, schema):
    # type: (Spec, typing.Optional[typing.Mapping[typing.Text, typing.Any]]) -> typing.Optional[typing.Set[typing.Text]]
    if schema is None or determine_object_type(schema) != ObjectType.SCHEMA:
        return None
    required, not_required = get_collapsed_properties_type_mappings(definition=schema, deref=swagger_spec.deref)
    return set(chain(iterkeys(required), iterkeys(not_required)))


StatusCodeSchema = typing.NamedTuple(
    'StatusCodeSchema', (
        ('status_code', typing.Text),
        ('mapping', EntityMapping[typing.Optional[typing.Mapping[typing.Text, typing.Any]]]),
    ),
)


def iterate_on_responses_status_codes(
    old_operation,  # type: typing.Mapping[typing.Text, typing.Any]
    new_operation,  # type: typing.Mapping[typing.Text, typing.Any]
):
    # type: (...) -> typing.Generator[StatusCodeSchema, None, None]
    old_status_code_schema_mapping = old_operation.get('responses') or {}
    new_status_code_schema_mapping = new_operation.get('responses') or {}

    common_response_codes = set(iterkeys(old_status_code_schema_mapping)).intersection(
        set(iterkeys(new_status_code_schema_mapping)),
    )
    # Compare schemas for the same status code only (TODO: what to do for old=default and new=404?)
    for status_code in common_response_codes:
        yield StatusCodeSchema(
            status_code=status_code,
            mapping=EntityMapping(
                old=old_status_code_schema_mapping[status_code].get('schema'),
                new=new_status_code_schema_mapping[status_code].get('schema'),
            ),
        )
