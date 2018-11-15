# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import argparse  # noqa: F401
import typing  # noqa: F401

from termcolor import colored

from swagger_spec_compatibility.cli.common import CLIProtocol
from swagger_spec_compatibility.rules.common import RuleRegistry


class _Namespace(CLIProtocol):
    rules = None  # type: typing.Iterable[typing.Text]


def execute(args):
    # type: (_Namespace) -> int
    rules_to_explain = {rule_name: RuleRegistry.rule(rule_name) for rule_name in args.rules}

    print(
        '{title}\n{rules_detail}'.format(
            title=colored('Rules explanation', attrs=['bold']),
            rules_detail='\n\t'.join(
                rule_class.explain()
                for rule_name, rule_class in rules_to_explain.items()
            ),
        ),
    )

    return 0


def add_sub_parser(subparsers):
    # type: (argparse._SubParsersAction) -> argparse.ArgumentParser
    return subparsers.add_parser('explain', help='explain selected rules')
