# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import typing  # noqa: F401

from bravado_core.spec import Spec  # noqa: F401

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import ErrorLevel


class DeletedEndpoint(BaseRule):
    def description(self):
        # type: () -> typing.Text
        return 'An endpoint has been removed. This change is not backward compatible as holders of stale swagger ' \
               'specs (like old mobile Apps) could continue to call the removed endpoint and this will cause an ' \
               'HTTP error status code (usually an HTTP/400 or HTTP/404)'

    def error_level(self, old_spec, new_spec):
        # type: (Spec, Spec) -> typing.Optional[ErrorLevel]
        return ErrorLevel.ERROR
