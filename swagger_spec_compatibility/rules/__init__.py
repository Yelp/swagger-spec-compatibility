# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401

from bravado_core.spec import Spec  # noqa: F401

from swagger_spec_compatibility.rules.added_enum_value_in_response import AddedEnumValueInRequest  # noqa: F401
from swagger_spec_compatibility.rules.added_properties_in_response_objects_with_additional_properties_set_to_false import AddedPropertiesInResponseObjectsWithAdditionalPropertiesSetToFalse  # noqa: F401,E501
from swagger_spec_compatibility.rules.added_required_property_in_request import AddedRequiredPropertyInRequest  # noqa: F401
from swagger_spec_compatibility.rules.changed_type import ChangedType  # noqa: F401
from swagger_spec_compatibility.rules.common import RuleProtocol  # noqa: F401
from swagger_spec_compatibility.rules.common import RuleRegistry  # noqa: F401
from swagger_spec_compatibility.rules.common import ValidationMessage  # noqa: F401
from swagger_spec_compatibility.rules.deleted_endpoint import DeletedEndpoint  # noqa: F401
from swagger_spec_compatibility.rules.removed_enum_value_from_request import RemovedEnumValueFromRequest  # noqa: F401
from swagger_spec_compatibility.rules.removed_properties_from_request_objects_with_additional_properties_set_to_false import RemovedPropertiesFromRequestObjectsWithAdditionalPropertiesSetToFalse  # noqa: F401,E501
from swagger_spec_compatibility.rules.removed_required_property_from_response import RemovedRequiredPropertyFromResponse  # noqa: F401


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
