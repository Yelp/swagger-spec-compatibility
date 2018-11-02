# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import typing  # noqa: F401
from abc import ABCMeta
from abc import abstractmethod
from enum import Enum

from bravado_core.spec import Spec  # noqa: F401
from six import with_metaclass


class StringEnum(str, Enum):
    """Enum where members are also (and must be) strings"""


class ErrorLevel(StringEnum):
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class RuleRegistry(ABCMeta):
    _REGISTRY = {}  # type: typing.MutableMapping[typing.Text, 'BaseRule']

    def __new__(mcs, name, bases, namespace):
        # type: (typing.Type['RuleRegistry'], str, typing.Tuple[type, ...], typing.Dict[str, typing.Any]) -> type
        new_cls = ABCMeta.__new__(mcs, name, bases, namespace)
        if name != 'BaseRule':
            RuleRegistry._REGISTRY[name] = new_cls()
        return new_cls

    @staticmethod
    def rules():
        # type: () -> typing.Iterable[typing.Text]
        return sorted(RuleRegistry._REGISTRY.keys())

    @staticmethod
    def has_rule(rule_name):
        # type: (typing.Text) -> bool
        return rule_name in RuleRegistry._REGISTRY

    @staticmethod
    def rule(rule_name):
        # type: (typing.Text) -> 'BaseRule'
        return RuleRegistry._REGISTRY[rule_name]


class BaseRule(with_metaclass(RuleRegistry)):
    @abstractmethod
    def description(self):
        # type: () -> typing.Text
        pass

    @abstractmethod
    def error_level(self, old_spec, new_spec):
        # type: (Spec, Spec) -> typing.Optional[ErrorLevel]
        pass
