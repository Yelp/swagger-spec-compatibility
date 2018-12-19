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
from swagger_spec_compatibility.walkers.request_parameters import RequestParametersWalker
from swagger_spec_compatibility.walkers.required_properties import RequiredPropertiesDifferWalker


class AddedRequiredPropertyInRequest(BaseRule):
    description = \
        'Adding a required property to an object used in requests leads ' \
        'client request to fail if the property is not present.'
    error_code = 'REQ-E001'
    error_level = Level.ERROR
    rule_type = RuleType.REQUEST_CONTRACT
    short_name = 'Added Required Property in Request contract'

    @classmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        request_parameters_paths = RequestParametersWalker(left_spec, right_spec).walk()

        # FIXME: the used walker is not able to merge together parameters defined in different locations
        for required_property_diff in RequiredPropertiesDifferWalker(left_spec, right_spec).walk():
            if not required_property_diff.mapping.new:
                continue
            if not is_path_in_top_level_paths(request_parameters_paths, required_property_diff.path):
                continue
            yield cls.validation_message(format_path(required_property_diff.path))
