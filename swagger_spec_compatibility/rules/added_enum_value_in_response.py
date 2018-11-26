# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401

from bravado_core.spec import Spec  # noqa: F401

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import ValidationMessage  # noqa: F401
from swagger_spec_compatibility.util import is_path_in_top_level_paths
from swagger_spec_compatibility.walkers import format_path  # noqa: F401
from swagger_spec_compatibility.walkers.enum_values import EnumValuesDifferWalker
from swagger_spec_compatibility.walkers.response_paths import ResponsePathsWalker


class AddedEnumValueInRequest(BaseRule):
    error_level = Level.ERROR
    error_code = 'E005'
    short_name = 'Added Enum value in Response contract'
    description = 'TODO'  # TODO: maci

    @classmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        response_paths = ResponsePathsWalker(left_spec, right_spec).walk()

        for enum_values_diff in EnumValuesDifferWalker(left_spec, right_spec).walk():
            if not enum_values_diff.mapping.new:
                continue
            if not is_path_in_top_level_paths(response_paths, enum_values_diff.path):
                continue
            yield cls.validation_message(format_path(enum_values_diff.path))
