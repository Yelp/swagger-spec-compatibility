# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from bravado_core.spec import Spec

from swagger_spec_compatibility.rules import DeletedEndpoint
from swagger_spec_compatibility.rules import ValidationMessage
from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.spec_utils import Endpoint
from swagger_spec_compatibility.spec_utils import HTTPVerb


def test_validate_succeed(minimal_spec_dict):
    assert list(DeletedEndpoint().validate(
        old_spec=Spec.from_dict(minimal_spec_dict),
        new_spec=Spec.from_dict(minimal_spec_dict),
    )) == []


def test_validate_return_an_error(minimal_spec_dict, simple_operation_dict):
    old_spec_dict = dict(
        minimal_spec_dict,
        paths={
            '/endpoint': {
                'get': simple_operation_dict,
            },
        },
    )
    assert list(DeletedEndpoint().validate(
        old_spec=Spec.from_dict(old_spec_dict),
        new_spec=Spec.from_dict(minimal_spec_dict),
    )) == [
        ValidationMessage(
            level=Level.ERROR,
            rule=DeletedEndpoint,
            reference=str(Endpoint(http_verb=HTTPVerb.GET, path='/endpoint')),
        ),
    ]
