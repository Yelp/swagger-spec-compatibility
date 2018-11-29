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
from swagger_spec_compatibility.walkers import format_path
from swagger_spec_compatibility.walkers.required_properties import RequiredPropertiesDifferWalker
from swagger_spec_compatibility.walkers.response_paths import ResponsePathsWalker


class RemovedRequiredPropertyFromResponse(BaseRule):
    description = \
        'Removing a required property from an object leads to false expectation on the client receiving the object. ' \
        'If the client is using "old" service\'s Swagger spec it will expect the property to be present and so it ' \
        'could throw errors. It could be valid to assume that the client won\'t perform response validation and this ' \
        'to unexpected errors while parsing the response and/or using the missing property.'
    error_level = Level.ERROR
    error_code = 'RES-E002'
    rule_type = RuleType.RESPONSE_CONTRACT
    short_name = 'Removed Required Property from Response contract'

    @classmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        response_paths = ResponsePathsWalker(left_spec, right_spec).walk()
        for required_property_diff in RequiredPropertiesDifferWalker(left_spec, right_spec).walk():
            if not required_property_diff.mapping.old:
                continue
            if not is_path_in_top_level_paths(response_paths, required_property_diff.path):
                continue
            yield cls.validation_message(format_path(required_property_diff.path))
