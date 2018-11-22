# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401

from bravado_core.spec import Spec  # noqa: F401
from six import text_type

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import ValidationMessage  # noqa: F401
from swagger_spec_compatibility.walkers import PathType  # noqa: F401
from swagger_spec_compatibility.walkers.required_properties import RequiredPropertiesDifferWalker
from swagger_spec_compatibility.walkers.response_paths import ResponsePathsWalker


class RemovedRequiredProperty(BaseRule):
    error_level = Level.ERROR
    error_code = 'E002'
    short_name = 'Removed Required Property'
    description = \
        'Removing a required property from an object leads to false expectation on the client receiving the object. ' \
        'If the client is using "old" service\'s Swagger spec it will expect the property to be present and so it could throw errors. ' \
        'It could be valid to assume that the client won\'t perform response validation and this leads to ' \
        'unexpected errors while parsing the response and/or using the missing property.'

    @staticmethod
    def _format_path(path):
        # type: (PathType) -> typing.Text
        return '#/{}'.format('/'.join(text_type(path_item) for path_item in path))

    @classmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        response_paths = [
            cls._format_path(path)
            for path in ResponsePathsWalker(left_spec, right_spec).walk()
        ]
        for required_property_diff in RequiredPropertiesDifferWalker(left_spec, right_spec).walk():
            if not required_property_diff.mapping.old:
                continue
            formatted_path = cls._format_path(required_property_diff.path)
            if any(
                formatted_path.startswith(path)
                for path in response_paths
            ):
                yield cls.validation_message(formatted_path)
