# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing

from bravado_core.spec import Spec
from bravado_core.util import determine_object_type
from bravado_core.util import ObjectType

from swagger_spec_compatibility.walkers import NoValue
from swagger_spec_compatibility.walkers import PathType
from swagger_spec_compatibility.walkers import SchemaWalker


class ResponsePathsWalker(SchemaWalker[PathType]):
    left_spec = None  # type: Spec
    right_spec = None  # type: Spec
    paths = None  # type: typing.Set[PathType]

    def should_path_be_walked_through(self, path):
        # type: (PathType) -> bool
        if not path:
            return True
        if path[0] != 'paths':
            return False
        if len(path) >= 4:
            # A valid path looks like ('paths', endpoint, http_verb, 'responses')
            return path[3] == 'responses'
        return True

    def __init__(
        self,
        left_spec,  # type: Spec
        right_spec,  # type: Spec
    ):
        # type: (...) -> None
        super(ResponsePathsWalker, self).__init__(left_spec=left_spec, right_spec=right_spec)
        self.paths = set()

    def dict_check(
        self,
        path,  # type: PathType
        left_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
        right_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
    ):
        # type: (...) -> typing.Iterable[PathType]
        if determine_object_type(left_dict) == ObjectType.RESPONSE or determine_object_type(right_dict) == ObjectType.RESPONSE:
            return (path,)
        else:
            return ()

    def list_check(
        self,
        path,  # type: PathType
        left_list,  # type: typing.Union[NoValue, typing.Sequence[typing.Any]]
        right_list,  # type: typing.Union[NoValue, typing.Sequence[typing.Any]]
    ):
        # type: (...) -> typing.Iterable[PathType]
        return ()

    def value_check(
        self,
        path,  # type: PathType
        left_value,  # type: typing.Any
        right_value,  # type: typing.Any
    ):
        # type: (...) -> typing.Iterable[PathType]
        return ()
