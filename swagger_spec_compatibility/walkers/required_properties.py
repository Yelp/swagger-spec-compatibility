# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing
from itertools import chain

from bravado_core.spec import Spec

from swagger_spec_compatibility.spec_utils import get_required_properties
from swagger_spec_compatibility.util import EntityMapping
from swagger_spec_compatibility.walkers import NoValue
from swagger_spec_compatibility.walkers import PathType
from swagger_spec_compatibility.walkers import SchemaWalker


def _different_properties_mapping(
    left_spec,  # type: Spec
    right_spec,  # type: Spec
    left_schema,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
    right_schema,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
):
    # type: (...) -> typing.Optional[EntityMapping[typing.Set[typing.Text]]]
    left_required = get_required_properties(swagger_spec=left_spec, schema=left_schema) or set()
    right_required = get_required_properties(swagger_spec=right_spec, schema=right_schema) or set()

    properties_appear_once = left_required.symmetric_difference(right_required)
    if not properties_appear_once:
        # The condition is true if left_required is empty and right_required is not empty or vice-versa
        return None
    else:
        return EntityMapping(
            old=properties_appear_once.intersection(left_required),
            new=properties_appear_once.intersection(right_required),
        )


class RequiredPropertiesDiff(typing.NamedTuple(
    'RequiredPropertiesDiff', (
        ('path', PathType),
        ('mapping', EntityMapping[typing.Set[typing.Text]]),
    ),
)):
    def fix_parameter_path(self, path, original_path):
        # type: (PathType, PathType) -> 'RequiredPropertiesDiff'
        return RequiredPropertiesDiff(
            path=tuple(chain(original_path, self.path[len(original_path):])),
            mapping=self.mapping,
        )


class RequiredPropertiesDifferWalker(SchemaWalker[RequiredPropertiesDiff]):
    left_spec = None  # type: Spec
    right_spec = None  # type: Spec
    diffs = None  # type: typing.List[RequiredPropertiesDiff]

    def __init__(
        self,
        left_spec,  # type: Spec
        right_spec,  # type: Spec
    ):
        # type: (...) -> None
        super(RequiredPropertiesDifferWalker, self).__init__(
            left_spec=left_spec,
            right_spec=right_spec,
        )

    def dict_check(
        self,
        path,  # type: PathType
        left_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
        right_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
    ):
        # type: (...) -> typing.Iterable[RequiredPropertiesDiff]
        different_properties_mapping = _different_properties_mapping(
            left_spec=self.left_spec,
            right_spec=self.right_spec,
            left_schema=None if isinstance(left_dict, NoValue) else left_dict,
            right_schema=None if isinstance(right_dict, NoValue) else right_dict,
        )
        if different_properties_mapping:
            return (
                RequiredPropertiesDiff(
                    path=path,
                    mapping=different_properties_mapping,
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
        # type: (...) -> typing.Iterable[RequiredPropertiesDiff]
        return ()

    def value_check(
        self,
        path,  # type: PathType
        left_value,  # type: typing.Any
        right_value,  # type: typing.Any
    ):
        # type: (...) -> typing.Iterable[RequiredPropertiesDiff]
        return ()
