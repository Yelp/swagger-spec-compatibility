# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401
from copy import deepcopy

import mock
import pytest

from swagger_spec_compatibility.util import EntityMapping
from swagger_spec_compatibility.util import Walker
from swagger_spec_compatibility.util import wrap


@pytest.mark.parametrize(
    'input_string, width, expected_result',
    [
        ('this is a string', 50, 'this is a string'),    # No wrapping needed
        ('this is a string', 5, 'this\nis a\nstring'),   # The lines are stripped
        ('this  is a string', 5, 'this\nis a\nstring'),  # Multiple spaces are condensed
        ('this_is_a_string', 5, 'this_is_a_string'),     # Words (characters with no spaces) will not be split
    ],
)
def test_wrap_provides_the_expected_string(input_string, width, expected_result):
    assert wrap(input_string, width=width) == expected_result


def test_EntityMapping_equality_and_hash():
    entity_mappint_1 = EntityMapping(old=1, new=2)
    entity_mappint_2 = EntityMapping(old=1, new=2)
    entity_mappint_3 = EntityMapping(old=1, new=3)

    assert hash(entity_mappint_1) == hash(entity_mappint_2)
    assert entity_mappint_1 == entity_mappint_2

    assert hash(entity_mappint_1) != hash(entity_mappint_3)
    assert entity_mappint_1 != entity_mappint_3


def test_EntityMapping_upacking_works():
    entity_mappint = EntityMapping(old=mock.sentinel.OLD, new=mock.sentinel.NEW)
    old, new = entity_mappint
    assert old == mock.sentinel.OLD
    assert new == mock.sentinel.NEW


def test_Walker_pass_through_all_the_items():
    left = {
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
    }  # type: typing.Dict[typing.Text, typing.Any]
    right = deepcopy(left)
    left['only_on_left'] = 1
    left['only_on_right'] = 1

    class DummySchemaWalker(Walker):
        recorded_calls = {
            'dict_check_paths': set(),
            'list_check_paths': set(),
            'value_check_paths': set(),
        }  # type: typing.MutableMapping[typing.Text, typing.Set[typing.Tuple[typing.Text, ...]]]

        def dict_check(self, path, left_dict, righ_dict):
            self.recorded_calls['dict_check_paths'].add(path)

        def list_check(self, path, left_list, righ_list):
            self.recorded_calls['list_check_paths'].add(path)

        def value_check(self, path, left_value, righ_value):
            self.recorded_calls['value_check_paths'].add(path)

        def walk_response(self):
            return self.recorded_calls

    assert DummySchemaWalker(left, right).walk() == {
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
            ('only_on_left',),
            ('only_on_right',),
        },
    }
