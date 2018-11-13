# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import typing  # noqa: F401

from bravado_core.spec import Spec  # noqa: F401

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import RuleMessage   # noqa: F401


class DeletedEndpoint(BaseRule):
    error_code = 'E001'
    short_name = 'Delete Endpoint'
    description = \
        'An endpoint has been removed. This change is not backward compatible as holders of stale swagger ' \
        'specs (like old mobile Apps) could continue to call the removed endpoint and this will cause an ' \
        'HTTP error status code (usually an HTTP/400 or HTTP/404)'

    def validate(self, old_spec, new_spec):
        # type: (Spec, Spec) -> typing.Iterable[RuleMessage]
        return ()
