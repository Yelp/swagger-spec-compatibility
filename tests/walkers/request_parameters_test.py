# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict
from swagger_spec_compatibility.walkers.request_parameters import RequestParametersWalker


def test_RequestParametersWalker_returns_no_paths_if_no_endpoints_defined(minimal_spec):
    assert set(RequestParametersWalker(minimal_spec, minimal_spec).walk()) == set()


def test_RequestParametersWalker_returns_paths_of_endpoints_parameters(minimal_spec, minimal_spec_dict):
    minimal_spec_dict['paths'] = {
        '/endpoint': {
            'get': {
                'parameters': [
                    {
                        'in': 'body',
                        'name': 'body',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                ],
                'responses': {
                    'default': {'description': ''},
                },
            },
            'put': {
                'responses': {
                    'default': {'description': ''},
                },
            },
        },
    }
    spec = load_spec_from_spec_dict(minimal_spec_dict)

    assert set(RequestParametersWalker(spec, spec).walk()) == {
        ('paths', '/endpoint', 'get', 'parameters', 0),
    }
