# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import os
import typing
import warnings
from argparse import ArgumentTypeError
from importlib import import_module
from os.path import abspath
from os.path import exists
from os.path import expanduser
from os.path import expandvars

import typing_extensions
from six.moves.urllib.parse import urljoin
from six.moves.urllib.request import pathname2url
from six.moves.urllib.request import url2pathname
from venusian import Scanner

from swagger_spec_compatibility.rules.common import BaseRule
from swagger_spec_compatibility.rules.common import RuleRegistry


_ENV_VARIABLE = str('CUSTOM_RULE_PACKAGES')


class CLIProtocol(typing_extensions.Protocol):
    command = None  # type: typing.Text
    func = None  # type: typing.Callable[['CLIProtocol'], int]


class CLIRulesProtocol(typing_extensions.Protocol):
    rules = None  # type: typing.Iterable[typing.Text]
    blacklist_rules = None  # type: typing.Iterable[typing.Text]


def uri(param):
    # type: (typing.Text) -> typing.Text
    if len(param.split('://')) > 1:
        return param

    path = expanduser(expandvars(url2pathname(param)))
    if exists(path):
        return urljoin('file:', pathname2url(abspath(path)))

    raise ArgumentTypeError('`{param}` is not an existing file and either a valid URI'.format(param=param))


def cli_rules():
    # type: () -> typing.List[typing.Text]
    return list(RuleRegistry.rule_names())


def rules(cli_args):
    # type: (CLIRulesProtocol) -> typing.Set[typing.Type[BaseRule]]
    return {
        RuleRegistry.rule(rule_name)
        for rule_name in cli_args.rules
        # The parser defines rules and blacklist_rules as mutual exclusive
        # so we're guaranteed to have at least one set to it's default value
        if rule_name not in cli_args.blacklist_rules
    }


def _get_rule_discovery_from_env():
    # type: () -> typing.List[typing.Text]
    return [
        value
        for value in (
            part.strip()
            for part in os.environ.get(_ENV_VARIABLE, '').split(',')
        )
        if value
    ]


def add_rule_discovery_argument(argument_parser):
    # type: (argparse.ArgumentParser) -> None
    argument_parser.add_argument(
        '-d', '--discover-rules-from',
        action='append',
        default=[_get_rule_discovery_from_env()],
        dest='packages_to_discover_rules_from',
        help='Non-standard packages to load rules from. '
             'The values can be defined as CSV in the {} '
             'environmental variable'.format(_ENV_VARIABLE),
        nargs='+',
    )


def pre_process_cli_to_discover_rules(argv=None):
    # type: (typing.Optional[typing.Sequence[typing.Text]]) -> None
    scanner = Scanner()
    rule_discovery_parser = argparse.ArgumentParser(add_help=False)
    add_rule_discovery_argument(rule_discovery_parser)
    rule_discovery_args, _ = rule_discovery_parser.parse_known_args(argv)
    for packages in (rule_discovery_args.packages_to_discover_rules_from or []):
        for package in packages:
            try:
                scanner.scan(import_module(package))
            except ImportError:
                warnings.warn(
                    RuntimeWarning('\'{}\' module, specified via the rule discovery CLI, is not found. Ignoring it.'.format(package)),
                )


def add_rules_arguments(argument_parser):
    # type: (argparse.ArgumentParser) -> None
    rules = cli_rules()
    if not rules:
        raise argument_parser.error('No rules are defined.')

    add_rule_discovery_argument(argument_parser)

    mutex_group = argument_parser.add_mutually_exclusive_group()
    mutex_group.add_argument(
        '-r', '--rules',
        action='append',
        choices=rules,
        dest='rules',
        help='Rules to apply for compatibility detection. (default: [%(choices)s])',
        metavar='RULE',
        nargs='+',
    )
    mutex_group.add_argument(
        '-b', '--blacklist-rules',
        action='append',
        choices=rules,
        dest='blacklist_rules',
        help='Rules to ignore for compatibility detection. (By default no rules are blacklisted)',
        metavar='RULE',
        nargs='+',
    )


def post_process_rules_cli_arguments(args):
    # type: (argparse.Namespace) -> argparse.Namespace
    def _extract_rules(field, default_value):
        # type: (typing.Text, typing.Iterable[typing.Text]) -> None
        if hasattr(args, field):  # pragma: no branch
            if getattr(args, field):
                setattr(
                    args, field,
                    list({rule for rules in getattr(args, field) for rule in rules}),
                )
            else:
                setattr(args, field, default_value)

    _extract_rules('rules', cli_rules())
    _extract_rules('blacklist_rules', [])

    return args
