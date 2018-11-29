# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing
from abc import ABCMeta
from abc import abstractmethod
from enum import IntEnum

import typing_extensions
from bravado_core.spec import Spec  # noqa: F401
from six import iterkeys
from six import itervalues
from six import with_metaclass
from termcolor import colored

from swagger_spec_compatibility.util import wrap


class RuleRegistry(ABCMeta):
    _REGISTRY = {}  # type: typing.MutableMapping[typing.Text, typing.Type['BaseRule']]

    @classmethod
    def _validate_class_attributes(mcs, cls):
        # type: (typing.Type['BaseRule']) -> None
        assert getattr(cls, 'error_code', None) is not None, 'error_code is a required class attribute for {}'.format(cls)
        assert getattr(cls, 'short_name', None) is not None, 'short_name is a required class attribute for {}'.format(cls)
        assert getattr(cls, 'description', None) is not None, 'description is a required class attribute for {}'.format(cls)
        assert getattr(cls, 'error_level', None) is not None, 'error_level is a required class attribute for {}'.format(cls)
        assert getattr(cls, 'rule_type', None) is not None, 'rule_type is a required class attribute for {}'.format(cls)

    @classmethod
    def _prevent_rule_duplication(mcs, cls):
        # type: (typing.Type['BaseRule']) -> None
        assert cls.error_code not in RuleRegistry._REGISTRY, \
            'Rule {} is already defined. Already existing: {} Trying to add: {}'.format(
                cls.error_code,
                RuleRegistry._REGISTRY[cls.error_code],
                cls,
            )

    @classmethod
    def _prevent_metaclass_usage_from_not_BaseRule_extensions(mcs, cls):
        # type: (typing.Type) -> None
        cls_fully_qualified_name = '{}.{}'.format(cls.__module__, cls.__name__)
        base_rule_fully_qualified_name = '{}.BaseRule'.format(mcs.__module__)
        assert (  # pragma: no branch
            cls_fully_qualified_name == base_rule_fully_qualified_name or
            any(base_rule_fully_qualified_name == '{}.{}'.format(c.__module__, c.__name__) for c in cls.__bases__)
        ), '{} metaclass should be used only by {}.BaseRule'.format(mcs, mcs.__module__)

    def __new__(mcs, name, bases, namespace):
        # type: (typing.Type['RuleRegistry'], str, typing.Tuple[type, ...], typing.Dict[str, typing.Any]) -> type
        new_cls = ABCMeta.__new__(mcs, name, bases, namespace)  # type: typing.Type['BaseRule']
        mcs._prevent_metaclass_usage_from_not_BaseRule_extensions(new_cls)

        if name != 'BaseRule':
            mcs._validate_class_attributes(new_cls)
            mcs._prevent_rule_duplication(new_cls)
            RuleRegistry._REGISTRY[new_cls.error_code] = new_cls
        return new_cls

    @staticmethod
    def rule_names():
        # type: () -> typing.Iterable[typing.Text]
        return sorted(iterkeys(RuleRegistry._REGISTRY))

    @staticmethod
    def rules():
        # type: () -> typing.Iterable[typing.Type['BaseRule']]
        return sorted(itervalues(RuleRegistry._REGISTRY), key=lambda rule: rule.error_code)

    @staticmethod
    def has_rule(rule_name):
        # type: (typing.Text) -> bool
        return rule_name in RuleRegistry._REGISTRY

    @staticmethod
    def rule(rule_name):
        # type: (typing.Text) -> typing.Type['BaseRule']
        return RuleRegistry._REGISTRY[rule_name]


class RuleType(IntEnum):
    REQUEST_CONTRACT = 0
    RESPONSE_CONTRACT = 1
    MISCELLANEOUS = 2


class Level(IntEnum):
    INFO = 0
    WARNING = 1
    ERROR = 2


class RuleProtocol(typing_extensions.Protocol):
    # Unique identifier of the rule
    error_code = None  # type: typing.Text
    # Short name of the rule. This will be visible on CLI in case the rule is triggered
    short_name = None  # type: typing.Text
    # Short description of the rationale of the rule. This will be visible on CLI only.
    description = None  # type: typing.Text
    # Error level associated to the rule
    error_level = None  # type: Level
    # Type of the rule associated
    rule_type = None  # type: RuleType

    @classmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable['ValidationMessage']
        pass


class ValidationMessage(typing.NamedTuple(
    '_ValidationMessage', (
        ('level', Level),
        ('rule', typing.Type[RuleProtocol]),
        ('reference', typing.Text),
    ),
)):
    def string_representation(self):
        # type: () -> typing.Text
        return '[{error_code}] {short_name} : {reference}'.format(
            error_code=self.rule.error_code,
            reference=self.reference,
            short_name=self.rule.short_name,
        )

    def json_representation(self):
        # type: () -> typing.Mapping[typing.Text, typing.Any]
        return {
            'error_code': self.rule.error_code,
            'reference': self.reference,
            'short_name': self.rule.short_name,
        }


class BaseRule(with_metaclass(RuleRegistry)):
    # Unique identifier of the rule
    error_code = None  # type: typing.Text
    # Short name of the rule. This will be visible on CLI in case the rule is triggered
    short_name = None  # type: typing.Text
    # Short description of the rationale of the rule. This will be visible on CLI only.
    description = None  # type: typing.Text
    # Error level associated to the rule
    error_level = None  # type: Level
    # Type of the rule associated
    rule_type = None  # type: RuleType

    def __init__(self):
        # type: () -> None
        raise RuntimeError('This class should not be initialized. The assumed usage is via class methods.')

    @classmethod
    @abstractmethod
    def validate(cls, left_spec, right_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        pass

    @classmethod
    def explain(cls):
        # type: () -> typing.Text
        return '[{error_code}] {short_name}:\n{rule_description}'.format(
            error_code=colored(cls.error_code, attrs=['bold']),
            short_name=colored(cls.short_name, color='cyan', attrs=['bold']),
            rule_description=wrap(cls.description, indent='\t'),
        )

    @classmethod
    def validation_message(cls, reference):
        # type: (typing.Text) -> ValidationMessage
        return ValidationMessage(
            level=cls.error_level,
            rule=cls,
            reference=reference,
        )
