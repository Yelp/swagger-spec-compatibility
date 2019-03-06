# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing
from copy import deepcopy

import mock
from bravado_core.spec import Spec

from swagger_spec_compatibility.walkers import PathType  # noqa: F401
from swagger_spec_compatibility.walkers import SchemaWalker


class DummySchemaWalker(SchemaWalker[typing.Tuple[str, PathType]]):
    left_spec = None  # type: Spec
    right_spec = None  # type: Spec
    additional = None  # type: bool
    recorded_calls = None  # type: typing.MutableMapping[typing.Text, typing.Set[typing.Tuple[typing.Text, ...]]]

    def dict_check(self, path, old_dict, new_dict):
        return (('dict_check_paths', path),)

    def list_check(self, path, old_list, new_list):
        return (('list_check_paths', path),)

    def value_check(self, path, old_value, new_value):
        return (('value_check_paths', path),)


class SkipDummySchemaWalker(DummySchemaWalker):
    def should_path_be_walked_through(self, path):
        # type: (PathType) -> bool
        paths_to_exclude = {
            ('dict',),
            ('list', 0, 'inner_dict'),
        }  # type: typing.Set[PathType]

        if not path:
            return True

        if any(
            path[:len(path_to_exclude)] == path_to_exclude
            for path_to_exclude in paths_to_exclude
        ):
            return False

        return True


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

    walker = DummySchemaWalker(spec, spec, additional=True)
    assert walker.left_spec == spec
    assert walker.right_spec == spec
    assert walker.additional is True
    assert set(walker.walk()) == {
        ('dict_check_paths', ('dict', 'dict_dict')),
        ('dict_check_paths', ('dict',)),
        ('dict_check_paths', ('list', 0)),
        ('dict_check_paths', ('list', 0, 'inner_dict')),
        ('dict_check_paths', ('list', 0, 'inner_dict', 'inner_dict_dict')),
        ('dict_check_paths', ('list', 1, 0)),
        ('dict_check_paths', ()),
        ('list_check_paths', ('dict', 'dict_list')),
        ('list_check_paths', ('list', 0, 'inner_dict', 'inner_dict_list')),
        ('list_check_paths', ('list', 1)),
        ('list_check_paths', ('list', 1, 1)),
        ('list_check_paths', ('list',)),
        ('value_check_paths', ('dict', 'dict_value')),
        ('value_check_paths', ('list', 0, 'inner_dict', 'inner_dict_value')),
        ('value_check_paths', ('list', 1, 2)),
        ('value_check_paths', ('list', 2)),
        ('value_check_paths', ('value',)),
    }


def test_SchemaWalker_skips_defined_paths():
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

    walker = SkipDummySchemaWalker(spec, spec, additional=True)
    assert walker.left_spec == spec
    assert walker.right_spec == spec
    assert walker.additional is True

    assert set(walker.walk()) == {
        ('dict_check_paths', ('list', 0)),
        ('dict_check_paths', ('list', 1, 0)),
        ('dict_check_paths', ()),
        ('list_check_paths', ('list', 1)),
        ('list_check_paths', ('list', 1, 1)),
        ('list_check_paths', ('list',)),
        ('value_check_paths', ('list', 1, 2)),
        ('value_check_paths', ('list', 2)),
        ('value_check_paths', ('value',)),
    }


def test_SchemaWalker_deals_with_recursive_objects():
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
    # Add recursion in deref_flattened_spec, this will not be present into the walked paths as
    # the object has already been traversed
    spec.deref_flattened_spec['level_recursive_schema'] = spec.deref_flattened_spec

    walker = DummySchemaWalker(spec, spec, additional=True)
    assert walker.left_spec == spec
    assert walker.right_spec == spec
    assert walker.additional is True
    assert set(walker.walk()) == {
        ('dict_check_paths', ('dict', 'dict_dict')),
        ('dict_check_paths', ('dict',)),
        ('dict_check_paths', ('dict',)),
        ('dict_check_paths', ('list', 0)),
        ('dict_check_paths', ('list', 0, 'inner_dict')),
        ('dict_check_paths', ('list', 0, 'inner_dict', 'inner_dict_dict')),
        ('dict_check_paths', ('list', 1, 0)),
        ('dict_check_paths', ()),
        ('list_check_paths', ('dict', 'dict_list')),
        ('list_check_paths', ('list', 0, 'inner_dict', 'inner_dict_list')),
        ('list_check_paths', ('list', 1)),
        ('list_check_paths', ('list', 1, 1)),
        ('list_check_paths', ('list',)),
        ('value_check_paths', ('dict', 'dict_value')),
        ('value_check_paths', ('list', 0, 'inner_dict', 'inner_dict_value')),
        ('value_check_paths', ('list', 1, 2)),
        ('value_check_paths', ('list', 2)),
        ('value_check_paths', ('value',)),
    }


def test_SchemaWalker_properly_deals_with_parameters():
    old_spec_dict = {
        'swagger': '2.0',
        'info': {
            'title': 'Test',
            'version': '1.0',
        },
        'paths': {
            '/endpoint': {
                'get': {
                    'parameters': [
                        {
                            'in': 'query',
                            'name': 'param1',
                            'type': 'string',
                        },
                        {
                            'in': 'query',
                            'name': 'param2',
                            'type': 'boolean',
                        },
                    ],
                    'responses': {
                        'default': {
                            'description': '',
                        },
                    },
                },
            },
        },
    }  # type: typing.Mapping[typing.Text, typing.Any]
    new_spec_dict = deepcopy(old_spec_dict)
    new_spec_dict['paths']['/endpoint']['get']['parameters'] = [new_spec_dict['paths']['/endpoint']['get']['parameters'][1]]
    old_spec = Spec.from_dict(spec_dict=old_spec_dict, origin_url='memory://')
    new_spec = Spec.from_dict(spec_dict=new_spec_dict, origin_url='memory://')

    walker = DummySchemaWalker(old_spec, new_spec)
    assert set(walker.walk()) == {
        # Ensure that parameters are indexed by parameter name instead of index in the array
        ('dict_check_paths', ()),
        ('dict_check_paths', ('info',)),
        ('dict_check_paths', ('paths',)),
        ('dict_check_paths', ('paths', '/endpoint')),
        ('dict_check_paths', ('paths', '/endpoint', 'get')),
        ('dict_check_paths', ('paths', '/endpoint', 'get', 'parameters', 'param2')),
        ('dict_check_paths', ('paths', '/endpoint', 'get', 'responses')),
        ('dict_check_paths', ('paths', '/endpoint', 'get', 'responses', 'default')),
        ('value_check_paths', ('info', 'title')),
        ('value_check_paths', ('info', 'version')),
        ('value_check_paths', ('paths', '/endpoint', 'get', 'parameters', 'param1')),
        ('value_check_paths', ('paths', '/endpoint', 'get', 'parameters', 'param2', 'in')),
        ('value_check_paths', ('paths', '/endpoint', 'get', 'parameters', 'param2', 'name')),
        ('value_check_paths', ('paths', '/endpoint', 'get', 'parameters', 'param2', 'type')),
        ('value_check_paths', ('paths', '/endpoint', 'get', 'responses', 'default', 'description')),
        ('value_check_paths', ('swagger',)),
    }


def test_fix_parameter_path_with_wrong_signature(recwarn):
    class ObjectWithWrongSignature(object):
        def __init__(self, value):
            self.value = value

        def fix_parameter_path(self):
            pass

    value = ObjectWithWrongSignature(1)
    walker = DummySchemaWalker(mock.Mock(spec=Spec), mock.Mock(spec=Spec))

    assert walker.fix_parameter_path(mock.sentinel.PATH, mock.sentinel.ORIGINAL_PATH, value) == value  # type: ignore
    assert len(recwarn.list) == 1
    assert recwarn.list[0].message.args[0] == \
        'Unexpected ObjectWithWrongSignature.fix_parameter_path signature. ' \
        'fix_parameter_path() got an unexpected keyword argument \'path\''
    assert recwarn.list[0].category == RuntimeWarning
