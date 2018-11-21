# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from swagger_spec_compatibility.rules import DeletedEndpoint
from swagger_spec_compatibility.spec_utils import Endpoint
from swagger_spec_compatibility.spec_utils import HTTPVerb
from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict


def test_validate_succeed(minimal_spec):
    assert list(DeletedEndpoint.validate(
        old_spec=minimal_spec,
        new_spec=minimal_spec,
    )) == []


def test_validate_return_an_error(minimal_spec_dict, simple_operation_dict, minimal_spec):
    old_spec_dict = dict(
        minimal_spec_dict,
        paths={
            '/endpoint': {
                'get': simple_operation_dict,
            },
        },
    )
    old_spec = load_spec_from_spec_dict(old_spec_dict)
    operation = old_spec.resources['endpoint'].operations['get_endpoint']
    assert list(DeletedEndpoint.validate(
        old_spec=old_spec,
        new_spec=minimal_spec,
    )) == [
        DeletedEndpoint.validation_message(
            reference=str(
                Endpoint(
                    http_verb=HTTPVerb.GET,
                    path='/endpoint',
                    operation=operation,
                ),
            ),
        ),
    ]
