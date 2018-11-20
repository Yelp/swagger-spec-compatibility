# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
from textwrap import dedent

from six import iteritems

from swagger_spec_compatibility.cli import explain  # noqa: F401
from swagger_spec_compatibility.cli import run  # noqa: F401
from swagger_spec_compatibility.cli.common import cli_rules
from swagger_spec_compatibility.rules import RuleRegistry
from swagger_spec_compatibility.util import wrap


_SUB_COMMAND_ASSOCIATED_FUNCTION_MAPPING = {
    explain.add_sub_parser: explain.execute,
    run.add_sub_parser: run.execute,
}


def parser():
    # type: () -> argparse.ArgumentParser

    parser = argparse.ArgumentParser(
        description=wrap(dedent("""
            Tool for the identification of backward incompatible changes between two swagger specs.

            The tool provides the following level of results:
            - WARNING: the Swagger specs are technically compatible but the are likely to break known Swagger implementations
            - ERROR: new Swagger spec does introduce a breaking change respect the old implementation
        """)),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    rules = cli_rules()
    parser.add_argument(
        '-r', '--rules',
        nargs='+',
        help='Rules to apply for compatibility detection. (default: %(default)s)',
        default=rules,
        choices=rules,
    )

    subparsers = parser.add_subparsers(help='help for sub-command', dest='command')
    subparsers.required = True
    for add_sub_command_parser, associated_function in iteritems(_SUB_COMMAND_ASSOCIATED_FUNCTION_MAPPING):
        add_sub_command_parser(subparsers).set_defaults(func=associated_function)

    if not RuleRegistry.rule_names():
        raise parser.error('No rules are defined.')

    return parser
