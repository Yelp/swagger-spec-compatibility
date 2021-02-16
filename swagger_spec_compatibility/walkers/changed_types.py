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


def _different_types_mapping(
    left_spec,  # type: Spec
    right_spec,  # type: Spec
    left_schema,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
    right_schema,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
):
    # type: (...) -> typing.Optional[EntityMapping[typing.Optional[typing.Text]]]
    left_type = left_schema.get('type') if left_schema is not None else None
    right_type = right_schema.get('type') if right_schema is not None else None

    if not left_type and left_spec.config['default_type_to_object']:  # Normalize type according to spec configuration
        left_type = 'object'
    if not right_type and right_spec.config['default_type_to_object']:  # Normalize type according to spec configuration
        right_type = 'object'

    if left_type == right_type:
        return None
    else:
        return EntityMapping(
            old=left_type,
            new=right_type,
        )


class ChangedTypesDiff(
    typing.NamedTuple(
        'ChangedTypesDiff', (
            ('path', PathType),
            ('mapping', EntityMapping[typing.Optional[typing.Text]]),
        ),
    ),
):
    def fix_parameter_path(self, path, original_path):
        # type: (PathType, PathType) -> 'ChangedTypesDiff'
        return ChangedTypesDiff(
            path=tuple(chain(original_path, self.path[len(original_path):])),
            mapping=self.mapping,
        )


class ChangedTypesDifferWalker(SchemaWalker[ChangedTypesDiff]):
    left_spec = None  # type: Spec
    right_spec = None  # type: Spec
    diffs = None  # type: typing.List[ChangedTypesDiff]

    def __init__(
        self,
        left_spec,  # type: Spec
        right_spec,  # type: Spec
    ):
        # type: (...) -> None
        super(ChangedTypesDifferWalker, self).__init__(
            left_spec=left_spec,
            right_spec=right_spec,
        )

    def dict_check(
        self,
        path,  # type: PathType
        left_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
        right_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
    ):
        # type: (...) -> typing.Iterable[ChangedTypesDiff]
        different_types_mapping = _different_types_mapping(
            left_spec=self.left_spec,
            right_spec=self.right_spec,
            left_schema=None if isinstance(left_dict, NoValue) else left_dict,
            right_schema=None if isinstance(right_dict, NoValue) else right_dict,
        )
        if different_types_mapping:
            return (
                ChangedTypesDiff(
                    path=path,
                    mapping=different_types_mapping,
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
        # type: (...) -> typing.Iterable[ChangedTypesDiff]
        return ()

    def value_check(
        self,
        path,  # type: PathType
        left_value,  # type: typing.Any
        right_value,  # type: typing.Any
    ):
        # type: (...) -> typing.Iterable[ChangedTypesDiff]
        return ()
