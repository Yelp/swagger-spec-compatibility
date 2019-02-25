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
from swagger_spec_compatibility.walkers.additional_properties import AdditionalPropertiesDifferWalker
from swagger_spec_compatibility.walkers.additional_properties import DiffType
from swagger_spec_compatibility.walkers.response_paths import ResponsePathsWalker


class AddedPropertiesInResponseObjectsWithAdditionalPropertiesSetToFalse(BaseRule):
    description = \
        'If the object is defined with additionalProperties set to False then the object will not allow presence of ' \
        'properties not defined on the properties section of the object definition. Adding a definition of a new ' \
        'property makes object sent from the server to the client be considered invalid by a client that is using ' \
        '"old" Swagger specs.'
    error_code = 'RES-E001'
    error_level = Level.ERROR
    rule_type = RuleType.RESPONSE_CONTRACT
    short_name = 'Added properties in an object with additionalProperties set to False used in response'

    @classmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        response_paths = ResponsePathsWalker(left_spec, right_spec).walk()
        for additional_properties_diff in AdditionalPropertiesDifferWalker(left_spec, right_spec).walk():
            if additional_properties_diff.diff_type != DiffType.PROPERTIES:
                continue
            if additional_properties_diff.properties and not additional_properties_diff.properties.new:
                continue
            if not is_path_in_top_level_paths(response_paths, additional_properties_diff.path):
                continue
            yield cls.validation_message(format_path(additional_properties_diff.path))
