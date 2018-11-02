# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import typing
from abc import ABCMeta
from abc import abstractmethod
from enum import IntEnum

from bravado_core.spec import Spec  # noqa: F401
from six import with_metaclass


class RuleRegistry(ABCMeta):
    _REGISTRY = {}  # type: typing.MutableMapping[typing.Text, 'BaseRule']

    def __new__(mcs, name, bases, namespace):
        # type: (typing.Type['RuleRegistry'], str, typing.Tuple[type, ...], typing.Dict[str, typing.Any]) -> type
        new_cls = ABCMeta.__new__(mcs, name, bases, namespace)
        if name != 'BaseRule':
            RuleRegistry._REGISTRY[name] = new_cls()
        return new_cls

    @staticmethod
    def rule_names():
        # type: () -> typing.Iterable[typing.Text]
        return sorted(RuleRegistry._REGISTRY.keys())

    @staticmethod
    def rule_classes():
        # type: () -> typing.Iterable['BaseRule']
        return sorted(RuleRegistry._REGISTRY.values())

    @staticmethod
    def has_rule(rule_name):
        # type: (typing.Text) -> bool
        return rule_name in RuleRegistry._REGISTRY

    @staticmethod
    def rule(rule_name):
        # type: (typing.Text) -> 'BaseRule'
        return RuleRegistry._REGISTRY[rule_name]


class Level(IntEnum):
    INFO = 0
    WARNING = 1
    ERROR = 2


RuleMessage = typing.NamedTuple(
    'RuleMessage', (
        ('level', Level),
        ('description', typing.Text),
    ),
)


class BaseRule(with_metaclass(RuleRegistry)):
    @abstractmethod
    def description(self):
        # type: () -> typing.Text
        pass

    @abstractmethod
    def validate(self, old_spec, new_spec):
        # type: (Spec, Spec) -> typing.Iterable[RuleMessage]
        pass
