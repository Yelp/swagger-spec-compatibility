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
from swagger_spec_compatibility.spec_utils import get_endpoints


class DeletedEndpoint(BaseRule):
    description = \
        'An endpoint has been removed. This change is not backward compatible as holders of stale swagger ' \
        'specs (like old mobile Apps) could continue to call the removed endpoint and this will cause an ' \
        'HTTP error status code (usually an HTTP/400 or HTTP/404)'
    error_code = 'MIS-E001'
    error_level = Level.ERROR
    rule_type = RuleType.MISCELLANEOUS
    short_name = 'Delete Endpoint'

    @classmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        endpoints_left_spec = get_endpoints(left_spec)
        endpoints_right_spec = get_endpoints(right_spec)

        for removed_endpoint in endpoints_left_spec - endpoints_right_spec:
            message = '{} {} \n\t\t'.format(
                removed_endpoint.http_verb.value,
                removed_endpoint.path,
            )
            yield cls.validation_message(message)
