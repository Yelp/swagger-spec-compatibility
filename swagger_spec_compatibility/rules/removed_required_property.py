# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401

from bravado_core.spec import Spec  # noqa: F401
from bravado_core.util import determine_object_type
from bravado_core.util import ObjectType
from six import text_type

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import ValidationMessage  # noqa: F401
from swagger_spec_compatibility.spec_utils import get_required_properties
from swagger_spec_compatibility.walkers import PathType  # noqa: F401
from swagger_spec_compatibility.walkers import SchemaWalker
from swagger_spec_compatibility.walkers import Walker


def _are_removed_required_properties_top_level_only(
    left_spec,  # type: Spec
    right_spec,  # type: Spec
    left_schema,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
    right_schema,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
):
    # type: (...) -> bool
    left_required = get_required_properties(swagger_spec=left_spec, schema=left_schema)
    right_required = get_required_properties(swagger_spec=right_spec, schema=right_schema)
    return bool(left_required and (not right_required or left_required - right_required))


class RemovedRequiredPropertyWalker(Walker[PathType]):
    left_spec = None  # type: Spec
    right_spec = None  # type: Spec

    def __init__(
        self,
        left,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
        right,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
        left_spec,  # type: Spec
        right_spec,  # type: Spec
    ):
        # type: (...) -> None
        super(RemovedRequiredPropertyWalker, self).__init__(
            left=left,
            right=right,
            left_spec=left_spec,
            right_spec=right_spec,
        )
        self.incriminated_paths = []  # type: typing.List[PathType]

    def dict_check(
        self,
        path,  # type: PathType
        left_dict,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
        right_dict,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
    ):
        # type: (...) -> None  # noqa
        if _are_removed_required_properties_top_level_only(
            left_spec=self.left_spec,
            right_spec=self.right_spec,
            left_schema=left_dict,
            right_schema=right_dict,
        ):
            self.incriminated_paths.append(path)

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
        # type: () -> typing.List[PathType]
        return self.incriminated_paths


class RemovedRequiredPropertyFromResponsesWalker(SchemaWalker[PathType]):
    left_spec = None  # type: Spec
    right_spec = None  # type: Spec

    def __init__(
        self,
        left_spec,  # type: Spec
        right_spec,  # type: Spec
    ):
        # type: (...) -> None
        super(RemovedRequiredPropertyFromResponsesWalker, self).__init__(left_spec=left_spec, right_spec=right_spec)
        self.incriminated_paths = []  # type: typing.List[PathType]

    def walk_response(self):
        # type: () -> typing.Iterable[PathType]
        return self.incriminated_paths

    def dict_check(
        self,
        path,  # type: PathType
        left_dict,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
        right_dict,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
    ):
        # type: (...) -> None  # noqa
        if left_dict and determine_object_type(left_dict) == ObjectType.RESPONSE:
            self.incriminated_paths.extend(
                path + ('schema',) + walker_path
                for walker_path in RemovedRequiredPropertyWalker(
                    left=left_dict.get('schema'),
                    right=right_dict.get('schema') if right_dict else {},
                    left_spec=self.left_spec,
                    right_spec=self.right_spec,

                ).walk()
            )

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
        # type: (...) -> None  # noqa
        pass


class RemovedRequiredProperty(BaseRule):
    error_level = Level.ERROR
    error_code = 'E002'
    short_name = 'Removed Required Property'
    description = \
        'Removing a required property from an object leads to false expectation on the client receiving the object. ' \
        'If the client is using "old" service\'s Swagger spec it will expect the property to be present and so it could throw errors. ' \
        'It could be valid to assume that the client won\'t perform response validation and this leads to ' \
        'unexpected errors while parsing the response and/or using the missing property.'

    @classmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        for incriminated_path in RemovedRequiredPropertyFromResponsesWalker(left_spec, right_spec).walk():
            yield cls.validation_message(
                '#/{}'.format('/'.join(text_type(path_item) for path_item in incriminated_path)),
            )
