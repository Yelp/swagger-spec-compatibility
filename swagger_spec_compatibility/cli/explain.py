# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse  # noqa: F401
import typing  # noqa: F401

from termcolor import colored

from swagger_spec_compatibility.cli.common import CLIProtocol
from swagger_spec_compatibility.cli.common import rules


class _Namespace(CLIProtocol):
    rules = None  # type: typing.Iterable[typing.Text]


def execute(cli_args):
    # type: (_Namespace) -> int
    print(
        '{title}\n{rules_detail}'.format(
            title=colored('Rules explanation', attrs=['bold']),
            rules_detail='\n'.join(
                rule.explain()
                for rule in sorted(rules(cli_args), key=lambda rule: rule.error_code)
            ),
        ),
    )

    return 0


def add_sub_parser(subparsers):
    # type: (argparse._SubParsersAction) -> argparse.ArgumentParser
    return subparsers.add_parser('explain', help='explain selected rules')
