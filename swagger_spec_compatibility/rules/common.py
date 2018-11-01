# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import typing  # noqa: F401
from abc import ABCMeta
from abc import abstractmethod
from enum import Enum

from six import with_metaclass


class StringEnum(str, Enum):
    """Enum where members are also (and must be) strings"""


class ErrorLevel(StringEnum):
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class RuleRegistry(ABCMeta):
    _REGISTRY = {}  # type: typing.MutableMapping[str, typing.Type['RuleRegistry']]

    def __new__(mcs, name, bases, namespace):
        # type: (typing.Type['RuleRegistry'], str, typing.Tuple[type, ...], typing.Dict[str, typing.Any]) -> type
        if name != 'BaseRule':
            RuleRegistry._REGISTRY[name] = mcs
        return ABCMeta.__new__(mcs, name, bases, namespace)

    @staticmethod
    def rules():
        # type: () -> typing.Iterable[str]
        return sorted(RuleRegistry._REGISTRY.keys())

    @staticmethod
    def has_rule(rule_name):
        # type: (str) -> bool
        return rule_name in RuleRegistry._REGISTRY

    @staticmethod
    def rule(rule_name):
        # type: (str) -> typing.Type['RuleRegistry']
        return RuleRegistry._REGISTRY[rule_name]


class BaseRule(with_metaclass(RuleRegistry)):
    @staticmethod
    @abstractmethod
    def description():
        # type: () -> typing.Text
        pass

    @staticmethod
    @abstractmethod
    def error_level():
        # type: () -> ErrorLevel
        pass
