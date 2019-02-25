# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401

from bravado_core.spec import Spec  # noqa: F401

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import RuleType
from swagger_spec_compatibility.rules.common import ValidationMessage  # noqa: F401
from swagger_spec_compatibility.util import is_path_in_top_level_paths
from swagger_spec_compatibility.walkers import format_path  # noqa: F401
from swagger_spec_compatibility.walkers.enum_values import EnumValuesDifferWalker
from swagger_spec_compatibility.walkers.request_parameters import RequestParametersWalker


class RemovedEnumValueFromRequest(BaseRule):
    description = 'Removing an enum value from a request parameter is backward incompatible as a previously valid ' \
                  'request will not be valid. This happens because a request containing the removed enum value, ' \
                  'valid according to the "old" Swagger spec, is not valid according to the new specs.'
    error_code = 'REQ-E002'
    error_level = Level.ERROR
    rule_type = RuleType.REQUEST_CONTRACT
    short_name = 'Removed Enum value from Request contract'

    @classmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        request_parameters_paths = RequestParametersWalker(left_spec, right_spec).walk()

        # FIXME: the used walker is not able to merge together parameters defined in different locations
        for enum_values_diff in EnumValuesDifferWalker(left_spec, right_spec).walk():
            if not enum_values_diff.mapping.old:
                continue
            if not is_path_in_top_level_paths(request_parameters_paths, enum_values_diff.path):
                continue
            yield cls.validation_message(format_path(enum_values_diff.path))
