# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing

from bravado_core.spec import Spec

from swagger_spec_compatibility.rules.common import RuleProtocol
from swagger_spec_compatibility.rules.common import RuleRegistry
from swagger_spec_compatibility.rules.common import ValidationMessage


class _ALL_RULES(object):
    def __str__(self):
        # type: () -> str
        return str('ALL_RULES')  # pragma: no cover  # This statement is present only to have a nicer REPL experience


def compatibility_status(
    old_spec,  # type: Spec
    new_spec,  # type: Spec
    rules=_ALL_RULES(),  # type: typing.Union[_ALL_RULES, typing.Iterable[typing.Type[RuleProtocol]]]
):
    # type: (...) -> typing.Mapping[typing.Type[RuleProtocol], typing.Iterable[ValidationMessage]]

    if isinstance(rules, _ALL_RULES):
        rules = RuleRegistry.rules()

    rules_to_error_level_mapping = {
        rule: list(rule.validate(left_spec=old_spec, right_spec=new_spec))
        for rule in rules
    }

    return rules_to_error_level_mapping
