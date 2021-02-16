# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing
from itertools import chain

from bravado_core.spec import Spec

from swagger_spec_compatibility.util import EntityMapping
from swagger_spec_compatibility.walkers import NoValue
from swagger_spec_compatibility.walkers import PathType
from swagger_spec_compatibility.walkers import SchemaWalker


def _different_enum_values_mapping(
    left_spec,  # type: Spec
    right_spec,  # type: Spec
    left_schema,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
    right_schema,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
):
    # type: (...) -> typing.Optional[EntityMapping[typing.Set[typing.Text]]]
    left_enum_values = (
        set(left_schema['enum'])
        if (left_schema and left_schema.get('type') == 'string' and 'enum' in left_schema)
        else set()
    )
    right_enum_values = (
        set(right_schema['enum'])
        if (right_schema and right_schema.get('type') == 'string' and 'enum' in right_schema)
        else set()
    )

    enum_values_appear_once = left_enum_values.symmetric_difference(right_enum_values)
    if not enum_values_appear_once:
        # The condition is true if left_required is empty and right_required is not empty or vice-versa
        return None
    else:
        return EntityMapping(
            old=enum_values_appear_once.intersection(left_enum_values),
            new=enum_values_appear_once.intersection(right_enum_values),
        )


class EnumValuesDiff(
    typing.NamedTuple(
        'EnumValuesDiff', (
            ('path', PathType),
            ('mapping', EntityMapping[typing.Any]),
        ),
    ),
):
    def fix_parameter_path(self, path, original_path):
        # type: (PathType, PathType) -> 'EnumValuesDiff'
        return EnumValuesDiff(
            path=tuple(chain(original_path, self.path[len(original_path):])),
            mapping=self.mapping,
        )


class EnumValuesDifferWalker(SchemaWalker[EnumValuesDiff]):
    left_spec = None  # type: Spec
    right_spec = None  # type: Spec

    def dict_check(
        self,
        path,  # type: PathType
        left_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
        right_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
    ):
        # type: (...) -> typing.Iterable[EnumValuesDiff]
        different_enum_values_mapping = _different_enum_values_mapping(
            left_spec=self.left_spec,
            right_spec=self.right_spec,
            left_schema=None if isinstance(left_dict, NoValue) else left_dict,
            right_schema=None if isinstance(right_dict, NoValue) else right_dict,
        )
        if different_enum_values_mapping is not None:
            return (
                EnumValuesDiff(
                    path=path,
                    mapping=different_enum_values_mapping,
                ),
            )
        else:
            return ()

    def list_check(
        self,
        path,  # type: PathType
        left_list,  # type: typing.Union[NoValue, typing.Sequence[typing.Any]]
        right_list,  # type: typing.Union[NoValue, typing.Sequence[typing.Any]]
    ):
        # type: (...) -> typing.Iterable[EnumValuesDiff]
        return ()

    def value_check(
        self,
        path,  # type: PathType
        left_value,  # type: typing.Any
        right_value,  # type: typing.Any
    ):
        # type: (...) -> typing.Iterable[EnumValuesDiff]
        return ()
