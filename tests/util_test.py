# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from swagger_spec_compatibility.util import EntityMapping
from swagger_spec_compatibility.util import is_path_in_top_level_paths
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


@pytest.mark.parametrize(
    'top_level_paths, path, expected_result',
    [
        ([tuple()], ('path_item',), True),
        ([('top',)], ('path_item',), False),
        ([('top',), ('path_item',)], ('path_item',), True),
        ([('top', 'inner')], ('top', 'different_inner'), False),
        ([('top', 'inner')], ('top', 'inner'), True),
        ([('top', 'inner')], ('top', 'inner', 'inner_inner'), True),
    ],
)
def test_is_path_in_top_level_paths(top_level_paths, path, expected_result):
    assert is_path_in_top_level_paths(top_level_paths, path) is expected_result
