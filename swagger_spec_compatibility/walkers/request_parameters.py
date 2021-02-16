# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing
from itertools import chain

from bravado_core.spec import Spec
from bravado_core.util import determine_object_type
from bravado_core.util import ObjectType

from swagger_spec_compatibility.walkers import NoValue
from swagger_spec_compatibility.walkers import PathType
from swagger_spec_compatibility.walkers import SchemaWalker


class RequestParametersWalker(SchemaWalker[PathType]):
    # TODO: update the name as it gets only the schemas of the parameters
    left_spec = None  # type: Spec
    right_spec = None  # type: Spec

    def fix_parameter_path(self, path, original_path, value):
        # type: (PathType, PathType, PathType) -> PathType
        return tuple(chain(original_path, value[len(original_path):]))

    def should_path_be_walked_through(self, path):
        # type: (PathType) -> bool
        if not path:
            return True

        # Request parameters could be defined in
        # - ('paths', endpoint, 'parameters', idx, 'schema')
        # - ('paths', endpoint, http_verb, 'parameters', idx, 'schema')
        if path[0] != 'paths':
            return False

        if len(path) >= 4 and (path[2] != 'parameters' and path[3] != 'parameters'):
            return False

        if len(path) >= 6 and (path[4] != 'schema' and path[5] != 'schema'):
            return False

        return True

    def __init__(
        self,
        left_spec,  # type: Spec
        right_spec,  # type: Spec
    ):
        # type: (...) -> None
        super(RequestParametersWalker, self).__init__(left_spec=left_spec, right_spec=right_spec)

    def dict_check(
        self,
        path,  # type: PathType
        left_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
        right_dict,  # type: typing.Union[NoValue, typing.Mapping[typing.Text, typing.Any]]
    ):
        # type: (...) -> typing.Iterable[PathType]
        if determine_object_type(left_dict) == ObjectType.PARAMETER or determine_object_type(right_dict) == ObjectType.PARAMETER:
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
