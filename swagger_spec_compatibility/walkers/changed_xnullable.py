# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing
from itertools import chain

from bravado_core.spec import Spec

from swagger_spec_compatibility.util import EntityMapping
from swagger_spec_compatibility.walkers import NO_VALUE
from swagger_spec_compatibility.walkers import NoValue
from swagger_spec_compatibility.walkers import PathType
from swagger_spec_compatibility.walkers import SchemaWalker


class ChangedXNullableDiff(typing.NamedTuple(
    'ChangedXNullableDiff', (
        ('path', PathType),
        ('mapping', EntityMapping[bool]),
    ),
)):
    def fix_parameter_path(self, path, original_path):
        # type: (PathType, PathType) -> 'ChangedXNullableDiff'
        return ChangedXNullableDiff(
            path=tuple(chain(original_path, self.path[len(original_path):])),
            mapping=self.mapping,
        )


class ChangedXNullableDifferWalker(SchemaWalker[ChangedXNullableDiff]):
    left_spec = None  # type: Spec
    right_spec = None  # type: Spec
    diffs = None  # type: typing.List[ChangedXNullableDiff]

    def __init__(
        self,
        left_spec,  # type: Spec
        right_spec,  # type: Spec
    ):
        # type: (...) -> None
        super(ChangedXNullableDifferWalker, self).__init__(
            left_spec=left_spec,
            right_spec=right_spec,
        )

    def dict_check(
        self,
        path,  # type: PathType
        left_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
        right_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
    ):
        # type: (...) -> typing.Iterable[ChangedXNullableDiff]
        return ()

    def list_check(
        self,
        path,  # type: PathType
        left_list,  # type: typing.Union[NoValue, typing.Sequence[typing.Any]]
        right_list,  # type: typing.Union[NoValue, typing.Sequence[typing.Any]]
    ):
        # type: (...) -> typing.Iterable[ChangedXNullableDiff]
        return ()

    def value_check(
        self,
        path,  # type: PathType
        left_value,  # type: typing.Any
        right_value,  # type: typing.Any
    ):
        # type: (...) -> typing.Iterable[ChangedXNullableDiff]
        if path[-1] == 'x-nullable':
            # Missing x-nullable attribute is equivalent to `x-nullable: False`
            if left_value is NO_VALUE:
                left_value = False
            if right_value is NO_VALUE:
                right_value = False
            if left_value != right_value:
                yield ChangedXNullableDiff(
                    path=path,
                    mapping=EntityMapping(
                        old=left_value,
                        new=right_value,
                    ),
                )
