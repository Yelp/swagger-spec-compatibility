# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401

from bravado_core.spec import Spec  # noqa: F401

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import RuleType
from swagger_spec_compatibility.rules.common import ValidationMessage   # noqa: F401
from swagger_spec_compatibility.util import is_path_in_top_level_paths
from swagger_spec_compatibility.walkers import format_path
from swagger_spec_compatibility.walkers.changed_types import ChangedTypesDifferWalker
from swagger_spec_compatibility.walkers.request_parameters import RequestParametersWalker
from swagger_spec_compatibility.walkers.response_paths import ResponsePathsWalker


class ChangedType(BaseRule):
    description = 'Changing the type of a field is not backward compatible as a client using "old" Swagger specs will ' \
                  'send the field with a different type leading the service to fail to validate the request. ' \
                  'On the other end, if the object containing the updated field is used in the response, ' \
                  'it will lead to unexpected client errors when parsing the response and/or using ' \
                  'the updated property.'
    error_code = 'MIS-E002'
    error_level = Level.ERROR
    rule_type = RuleType.MISCELLANEOUS
    short_name = 'Changed type'

    @classmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]

        request_parameter_paths = RequestParametersWalker(left_spec, right_spec).walk()
        response_paths = ResponsePathsWalker(left_spec, right_spec).walk()

        for changed_types_diff in ChangedTypesDifferWalker(left_spec, right_spec).walk():
            if (
                not is_path_in_top_level_paths(request_parameter_paths, changed_types_diff.path) and
                not is_path_in_top_level_paths(response_paths, changed_types_diff.path)
            ):
                continue
            yield cls.validation_message(format_path(changed_types_diff.path))
