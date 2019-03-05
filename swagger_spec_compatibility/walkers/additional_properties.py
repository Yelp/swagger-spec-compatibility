# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing
from enum import Enum
from itertools import chain

from bravado_core.spec import Spec

from swagger_spec_compatibility.spec_utils import get_properties
from swagger_spec_compatibility.util import EntityMapping
from swagger_spec_compatibility.walkers import NoValue
from swagger_spec_compatibility.walkers import PathType
from swagger_spec_compatibility.walkers import SchemaWalker


class DiffType(Enum):
    PROPERTIES = 0
    VALUE = 1


class AdditionalPropertiesDiff(typing.NamedTuple(
    'AdditionalPropertiesDiff', (
        ('path', PathType),
        ('diff_type', DiffType),
        ('additionalProperties', typing.Optional[EntityMapping[typing.Union[bool, typing.Mapping[typing.Text, typing.Any]]]]),
        ('properties', typing.Optional[EntityMapping[typing.Set[typing.Text]]]),
    ),
)):
    def fix_parameter_path(self, path, original_path):
        # type: (PathType, PathType) -> 'AdditionalPropertiesDiff'
        return AdditionalPropertiesDiff(
            path=tuple(chain(original_path, self.path[len(original_path):])),
            diff_type=self.diff_type,
            additionalProperties=self.additionalProperties,
            properties=self.properties,
        )


def _evaluate_additional_properties_diffs(
    path,  # type: PathType
    left_spec,  # type: Spec
    right_spec,  # type: Spec
    left_schema,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
    right_schema,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
):
    # type: (...) -> typing.List[AdditionalPropertiesDiff]
    result = []  # type: typing.List[AdditionalPropertiesDiff]
    left_additional_properties = None if left_schema is None else left_schema.get('additionalProperties', True)
    right_additional_properties = None if right_schema is None else right_schema.get('additionalProperties', True)
    left_properties = get_properties(left_spec, left_schema) or set()
    right_properties = get_properties(right_spec, right_schema) or set()
    properties_appear_once = left_properties.symmetric_difference(right_properties)

    if left_additional_properties == {}:  # Normalize additional properties
        left_additional_properties = True
    if right_additional_properties == {}:  # Normalize additional properties
        right_additional_properties = True

    if left_additional_properties != right_additional_properties:
        result.append(AdditionalPropertiesDiff(
            path=path,
            diff_type=DiffType.VALUE,
            additionalProperties=EntityMapping(
                # casting here is safe as swagger specs are assumed to be valid and bool or dict are the only possible types
                old=typing.cast(typing.Union[bool, typing.Mapping[typing.Text, typing.Any]], left_additional_properties),
                new=typing.cast(typing.Union[bool, typing.Mapping[typing.Text, typing.Any]], right_additional_properties),
            ),
            properties=None,
        ))

    if (left_additional_properties is False or right_additional_properties is False) and properties_appear_once:
        result.append(AdditionalPropertiesDiff(
            path=path,
            diff_type=DiffType.PROPERTIES,
            additionalProperties=None,
            properties=EntityMapping(
                old=properties_appear_once.intersection(left_properties),
                new=properties_appear_once.intersection(right_properties),
            ),
        ))

    return result


class AdditionalPropertiesDifferWalker(SchemaWalker[AdditionalPropertiesDiff]):
    left_spec = None  # type: Spec
    right_spec = None  # type: Spec
    additionalPropertiesValue = None  # type: typing.Union[bool, typing.Mapping[typing.Text, typing.Any]]
    diffs = None  # type: typing.List[AdditionalPropertiesDiff]

    def dict_check(
        self,
        path,  # type: PathType
        left_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
        right_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
    ):
        # type: (...) -> typing.Iterable[AdditionalPropertiesDiff]

        return _evaluate_additional_properties_diffs(
            path=path,
            left_spec=self.left_spec,
            right_spec=self.right_spec,
            left_schema=None if isinstance(left_dict, NoValue) else left_dict,
            right_schema=None if isinstance(right_dict, NoValue) else right_dict,
        )

    def list_check(
        self,
        path,  # type: PathType
        left_list,  # type: typing.Union[NoValue, typing.Sequence[typing.Any]]
        right_list,  # type: typing.Union[NoValue, typing.Sequence[typing.Any]]
    ):
        # type: (...) -> typing.Iterable[AdditionalPropertiesDiff]
        return ()

    def value_check(
        self,
        path,  # type: PathType
        left_value,  # type: typing.Any
        right_value,  # type: typing.Any
    ):
        # type: (...) -> typing.Iterable[AdditionalPropertiesDiff]
        return ()
