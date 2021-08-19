# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing
from multiprocessing import Pool

from bravado_core.spec import Spec

from swagger_spec_compatibility.rules.common import RuleProtocol
from swagger_spec_compatibility.rules.common import RuleRegistry
from swagger_spec_compatibility.rules.common import ValidationMessage


class _ALL_RULES(object):
    def __str__(self):
        # type: () -> str
        return str('ALL_RULES')  # pragma: no cover  # This statement is present only to have a nicer REPL experience


def validate_rules(
    old_spec,  # type: Spec
    new_spec,  # type: Spec
    rule,  # type: typing.Type[RuleProtocol]
):
    # type: (...) -> typing.Iterable[ValidationMessage]
    return list(rule.validate(left_spec=old_spec, right_spec=new_spec))   # pragma: no cover


def multi_run_wrapper(
    args,  # type: typing.Tuple[Spec, Spec, typing.Type[RuleProtocol]]
):
    # type: (...) -> typing.Iterable[ValidationMessage]
    return validate_rules(*args)   # pragma: no cover


def compatibility_status(
    old_spec,  # type: Spec
    new_spec,  # type: Spec
    rules=_ALL_RULES(),  # type: typing.Union[_ALL_RULES, typing.Iterable[typing.Type[RuleProtocol]]]
):
    # type: (...) -> typing.Mapping[typing.Type[RuleProtocol], typing.Iterable[ValidationMessage]]

    if isinstance(rules, _ALL_RULES):
        rules = RuleRegistry.rules()

    rules_list = list(rules)

    args_list = [
        (old_spec, new_spec, rule)
        for rule in rules_list
    ]

    pool = Pool(processes=4)
    results = pool.map(multi_run_wrapper, args_list)
    pool.terminate()

    rules_to_error_level_mapping = {
        rules_list[i]: results[i]
        for i in range(len(rules_list))
    }

    return rules_to_error_level_mapping
