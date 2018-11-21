# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401

from bravado_core.spec import Spec  # noqa: F401

from swagger_spec_compatibility.rules.common import RuleProtocol  # noqa: F401
from swagger_spec_compatibility.rules.common import RuleRegistry  # noqa: F401
from swagger_spec_compatibility.rules.common import ValidationMessage  # noqa: F401
from swagger_spec_compatibility.rules.deleted_endpoint import DeletedEndpoint  # noqa: F401
from swagger_spec_compatibility.rules.removed_required_property import RemovedRequiredProperty  # noqa: F401


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
        rule: list(rule.validate(old_spec=old_spec, new_spec=new_spec))
        for rule in rules
    }

    return rules_to_error_level_mapping
