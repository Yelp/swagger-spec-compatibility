# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import argparse  # noqa: F401
import typing

from termcolor import colored

from swagger_spec_compatibility.cli.common import wrap
from swagger_spec_compatibility.rules.common import RuleRegistry


_Namespace = typing.NamedTuple(
    '_Namespace', [
        ('command', typing.Text),
        ('func', typing.Callable[[typing.Iterable[typing.Any]], None]),
        ('rules', typing.Iterable[typing.Text]),
    ],
)


def execute(args):
    # type: (_Namespace) -> int
    rules_to_explain = {rule_name: RuleRegistry.rule(rule_name) for rule_name in args.rules}

    print(
        '{title}\n{rules_detail}'.format(
            title=colored('Rules explanation', attrs=['bold']),
            count=len(rules_to_explain),
            rules_detail='\n\t'.join(
                '{rule_name}:\n{rule_description}'.format(
                    rule_name=colored(rule_name, color='cyan', attrs=['bold']),
                    rule_description=wrap(rule_class.description(), indent='\t'),
                )
                for rule_name, rule_class in rules_to_explain.items()
            ),
        ),
    )

    return 0


def add_sub_parser(subparsers):
    # type: (argparse._SubParsersAction) -> argparse.ArgumentParser
    return subparsers.add_parser('explain', help='explain selected rules')
