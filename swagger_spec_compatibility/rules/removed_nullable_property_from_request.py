# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing

from bravado_core.spec import Spec

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import RuleType
from swagger_spec_compatibility.rules.common import ValidationMessage
from swagger_spec_compatibility.util import is_path_in_top_level_paths
from swagger_spec_compatibility.walkers import format_path
from swagger_spec_compatibility.walkers.changed_xnullable import ChangedXNullableDifferWalker
from swagger_spec_compatibility.walkers.request_parameters import RequestParametersWalker


class RemovedNullablePropertyFromRequest(BaseRule):
    description = 'TODO'
    error_code = 'REQ-E004'
    error_level = Level.ERROR
    rule_type = RuleType.REQUEST_CONTRACT
    short_name = 'TODO'
    documentation_link = None

    @classmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        request_parameters_paths = RequestParametersWalker(left_spec, right_spec).walk()

        # FIXME: the used walker is not able to merge together parameters defined in different locations
        for nullable_values_diff in ChangedXNullableDifferWalker(left_spec, right_spec).walk():
            if not nullable_values_diff.mapping.old:
                continue
            if not is_path_in_top_level_paths(request_parameters_paths, nullable_values_diff.path):
                continue
            yield cls.validation_message(format_path(nullable_values_diff.path))
