# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from swagger_spec_compatibility.spec_utils import load_spec_from_spec_dict
from swagger_spec_compatibility.walkers.response_paths import ResponsePathsWalker


def test_ResponsePathsWalker_returns_no_paths_if_no_endpoints_defined(minimal_spec):
    assert ResponsePathsWalker(minimal_spec, minimal_spec).walk() == []


def test_ResponsePathsWalker_returns_paths_of_endpoints_responses(minimal_spec, minimal_spec_dict):
    minimal_spec_dict['paths'] = {
        '/endpoint': {
            'get': {
                'responses': {
                    '200': {'description': ''},
                    'default': {'description': ''},
                },
            },
            'put': {
                'responses': {
                    '403': {'description': ''},
                },
            },
        },
    }
    spec = load_spec_from_spec_dict(minimal_spec_dict)

    assert set(ResponsePathsWalker(spec, spec).walk()) == {
        ('paths', '/endpoint', 'get', 'responses', '200'),
        ('paths', '/endpoint', 'get', 'responses', 'default'),
        ('paths', '/endpoint', 'put', 'responses', '403'),
    }
