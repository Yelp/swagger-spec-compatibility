# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing

from bravado_core.spec import Spec  # noqa: F401

from swagger_spec_compatibility.util import EntityMapping
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


EnumValuesDiff = typing.NamedTuple(
    'EnumValuesDiff', (
        ('path', PathType),
        ('mapping', EntityMapping[typing.Any]),
    ),
)


class EnumValuesDifferWalker(SchemaWalker[EnumValuesDiff]):
    left_spec = None  # type: Spec
    right_spec = None  # type: Spec
    diffs = None  # type: typing.List[EnumValuesDiff]

    def __init__(
        self,
        left_spec,  # type: Spec
        right_spec,  # type: Spec
    ):
        # type: (...) -> None
        super(EnumValuesDifferWalker, self).__init__(
            left_spec=left_spec,
            right_spec=right_spec,
        )
        self.diffs = []

    def dict_check(
        self,
        path,  # type: PathType
        left_dict,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
        right_dict,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
    ):
        # type: (...) -> None  # noqa
        different_enum_values_mapping = _different_enum_values_mapping(
            left_spec=self.left_spec,
            right_spec=self.right_spec,
            left_schema=left_dict,
            right_schema=right_dict,
        )
        if different_enum_values_mapping is not None:
            self.diffs.append(EnumValuesDiff(
                path=path,
                mapping=different_enum_values_mapping,
            ))

    def list_check(
        self,
        path,  # type: PathType
        left_list,  # type: typing.Optional[typing.Sequence[typing.Any]]
        right_list,  # type: typing.Optional[typing.Sequence[typing.Any]]
    ):
        # type: (...) -> None  # noqa
        pass

    def value_check(
        self,
        path,  # type: PathType
        left_value,  # type: typing.Any
        right_value,  # type: typing.Any
    ):
        # type: (...) -> None
        pass

    def walk_response(self):
        # type: () -> typing.List[EnumValuesDiff]
        return self.diffs
