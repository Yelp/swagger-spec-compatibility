# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401

from bravado_core.spec import Spec  # noqa: F401

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import ValidationMessage  # noqa: F401


class RemovedRequiredProperty(BaseRule):
    error_level = Level.ERROR
    error_code = 'E002'
    short_name = 'Removed Required Property'
    description = \
        'Removing a required property from an object leads to false expectation on the client receiving the object. ' \
        'If the client is using "old" service\'s Swagger spec it will expect the property to be present and so it could throw errors. ' \
        'It could be valid to assume that the client won\'t perform response validation and this leads to ' \
        'unexpected errors while parsing the response and/or using the missing property.'

    @classmethod
    def validate(cls, old_spec, new_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        return ()
