# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import typing
from abc import ABCMeta
from abc import abstractmethod
from enum import IntEnum

import typing_extensions
from bravado_core.spec import Spec  # noqa: F401
from six import with_metaclass
from termcolor import colored

from swagger_spec_compatibility.util import wrap


class RuleRegistry(ABCMeta):
    _REGISTRY = {}  # type: typing.MutableMapping[typing.Text, typing.Type['BaseRule']]

    def __new__(mcs, name, bases, namespace):
        # type: (typing.Type['RuleRegistry'], str, typing.Tuple[type, ...], typing.Dict[str, typing.Any]) -> type
        new_cls = ABCMeta.__new__(mcs, name, bases, namespace)
        if name != 'BaseRule':
            RuleRegistry._REGISTRY[name] = new_cls
        return new_cls

    @staticmethod
    def rule_names():
        # type: () -> typing.Iterable[typing.Text]
        return sorted(RuleRegistry._REGISTRY.keys())

    @staticmethod
    def rules():
        # type: () -> typing.Iterable[typing.Type['BaseRule']]
        return sorted(RuleRegistry._REGISTRY.values(), key=lambda rule: rule.error_code)

    @staticmethod
    def has_rule(rule_name):
        # type: (typing.Text) -> bool
        return rule_name in RuleRegistry._REGISTRY

    @staticmethod
    def rule(rule_name):
        # type: (typing.Text) -> typing.Type['BaseRule']
        return RuleRegistry._REGISTRY[rule_name]


class Level(IntEnum):
    INFO = 0
    WARNING = 1
    ERROR = 2


class RequiredAttributeMixin(object):
    def __new__(cls):
        # type: (typing.Any) -> typing.Any
        assert getattr(cls, 'error_code', None) is not None
        assert getattr(cls, 'short_name', None) is not None
        assert getattr(cls, 'description', None) is not None
        return super(RequiredAttributeMixin, cls).__new__(cls)


class RuleProtocol(typing_extensions.Protocol):
    # Unique identifier of the rule
    error_code = None  # type: typing.Text
    # Short name of the rule. This will be visible on CLI in case the rule is triggered
    short_name = None  # type: typing.Text
    # Short description of the rationale of the rule. This will be visible on CLI only.
    description = None  # type: typing.Text

    @classmethod
    def validate(cls, old_spec, new_spec):
        # type: (Spec, Spec) -> typing.Iterable['ValidationMessage']
        pass


ValidationMessage = typing.NamedTuple(
    'ValidationMessage', (
        ('level', Level),
        ('rule', typing.Type[RuleProtocol]),
        ('reference', typing.Text),
    ),
)


class BaseRule(with_metaclass(RuleRegistry, RequiredAttributeMixin)):
    # Unique identifier of the rule
    error_code = None  # type: typing.Text
    # Short name of the rule. This will be visible on CLI in case the rule is triggered
    short_name = None  # type: typing.Text
    # Short description of the rationale of the rule. This will be visible on CLI only.
    description = None  # type: typing.Text

    @classmethod
    @abstractmethod
    def validate(cls, old_spec, new_spec):
        # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
        pass

    @classmethod
    def explain(cls):
        # type: () -> typing.Text
        return '{short_name} [{error_code}]:\n{rule_description}'.format(
            short_name=colored(cls.short_name, color='cyan', attrs=['bold']),
            error_code=cls.error_code,
            rule_description=wrap(cls.description, indent='\t'),
        )
