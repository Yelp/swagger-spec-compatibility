# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import typing  # noqa: F401

from bravado.client import SwaggerClient
from bravado_core.spec import Spec  # noqa: F401

from swagger_spec_compatibility.rules.common import BaseRule  # noqa: F401
from swagger_spec_compatibility.rules.common import RuleMessage  # noqa: F401
from swagger_spec_compatibility.rules.common import RuleRegistry  # noqa: F401
from swagger_spec_compatibility.rules.deleted_endpoint import DeletedEndpoint  # noqa: F401


class _ALL_RULES(object):
    pass


def _load_spec_from_uri(uri):
    # type: (typing.Text) -> Spec
    return SwaggerClient.from_url(uri, config={'internally_dereference_refs': True}).swagger_spec


def compatibility_status(
    old_spec_uri,  # type: typing.Text
    new_spec_uri,  # type: typing.Text
    rules=_ALL_RULES(),  # type: typing.Union[_ALL_RULES, typing.Iterable[BaseRule]]
    strict=False,  # type: bool
):
    # type: (...) -> typing.Mapping[BaseRule, typing.Iterable[RuleMessage]]

    old_spec = _load_spec_from_uri(old_spec_uri)
    new_spec = _load_spec_from_uri(new_spec_uri)

    if isinstance(rules, _ALL_RULES):
        rules = RuleRegistry.rule_classes()

    rules_to_error_level_mapping = {
        rule: rule.validate(old_spec=old_spec, new_spec=new_spec)
        for rule in rules
    }

    return rules_to_error_level_mapping
