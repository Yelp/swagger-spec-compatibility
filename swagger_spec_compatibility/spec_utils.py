# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401
from enum import Enum

from bravado.client import SwaggerClient
from bravado_core.operation import Operation  # noqa: F401
from bravado_core.spec import Spec  # noqa: F401

from swagger_spec_compatibility.cache import typed_lru_cache


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
