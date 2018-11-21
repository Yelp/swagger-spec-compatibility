# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401

import mock
from bravado_core.spec import Spec

from swagger_spec_compatibility.walkers import SchemaWalker


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
                {
                    'inner_dict': {
                        'inner_dict_dict': {},
                        'inner_dict_list': [],
                        'inner_dict_value': None,
                    },
                },
                [
                    {},
                    [],
                    None,
                ],
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
    print(walker.walk())
    assert walker.walk() == {
        'dict_check_paths': {
            ('dict', 'dict_dict'),
            ('dict',),
            ('list', 0),
            ('list', 0, 'inner_dict'),
            ('list', 0, 'inner_dict', 'inner_dict_dict'),
            ('list', 1, 0),
            (),
        },
        'list_check_paths': {
            ('dict', 'dict_list'),
            ('list', 0, 'inner_dict', 'inner_dict_list'),
            ('list', 1),
            ('list', 1, 1),
            ('list',),
        },
        'value_check_paths': {
            ('dict', 'dict_value'),
            ('list', 0, 'inner_dict', 'inner_dict_value'),
            ('list', 1, 2),
            ('list', 2),
            ('value',),
        },
    }
