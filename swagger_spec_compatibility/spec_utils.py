# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401

from bravado.client import SwaggerClient
from bravado_core.operation import Operation  # noqa: F401
from bravado_core.spec import Spec  # noqa: F401

from swagger_spec_compatibility.cache import typed_lru_cache
from swagger_spec_compatibility.util import StringEnum


class HTTPVerb(StringEnum):
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
    ),
)):

    @staticmethod
    def from_swagger_operation(operation):
        # type: (Operation) -> 'Endpoint'
        return Endpoint(
            http_verb=HTTPVerb.from_swagger_operation(operation),
            path=operation.path_name,
        )


@typed_lru_cache
def load_spec_from_uri(uri):
    # type: (typing.Text) -> Spec
    return SwaggerClient.from_url(uri, config={'internally_dereference_refs': True}).swagger_spec


@typed_lru_cache
def get_operations(spec):
    # type: (Spec) -> typing.Set[Operation]
    return {
        operation
        for resource in spec.resources.values()
        for operation in resource.operations.values()
    }


@typed_lru_cache
def get_endpoints(spec):
    # type: (Spec) -> typing.Set[Endpoint]
    return {
        Endpoint.from_swagger_operation(operation)
        for operation in get_operations(spec)
    }
