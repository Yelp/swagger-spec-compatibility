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
from swagger_spec_compatibility.walkers import format_path
from swagger_spec_compatibility.walkers.additional_properties import AdditionalPropertiesDifferWalker
from swagger_spec_compatibility.walkers.additional_properties import DiffType


class ChangedAdditionalPropertiesToFalse(BaseRule):
    description = \
        'If the object is defined with additionalProperties set to False then the object will not allow presence of ' \
        'properties not defined on the properties section of the object definition. ' \
        'Changing additionalProperties from True to False makes objects sent from a client, ' \
        'that contain additional properties and were permitted by the "old" Swagger specs, ' \
        'to the server be considered invalid by the backend.'
    error_code = 'REQ-E004'
    error_level = Level.ERROR
    rule_type = RuleType.REQUEST_CONTRACT
    short_name = 'Changing additionalProperties to False for a request parameter'

    @classmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        for additional_properties_diff in AdditionalPropertiesDifferWalker(left_spec, right_spec).walk():
            if additional_properties_diff.diff_type != DiffType.VALUE:
                continue
            if (
                additional_properties_diff.additionalProperties is not None
                and additional_properties_diff.additionalProperties.new is False
            ):
                yield cls.validation_message(format_path(additional_properties_diff.path))
