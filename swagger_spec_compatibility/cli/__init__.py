# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import argparse
import typing  # noqa: F401
from textwrap import dedent
from textwrap import TextWrapper

from swagger_spec_compatibility.cli import explain  # noqa: F401
from swagger_spec_compatibility.cli import run  # noqa: F401
from swagger_spec_compatibility.rules import RuleRegistry


_SUB_COMMAND_ASSOCIATED_FUNCTION_MAPPING = {
    explain.add_sub_parser: explain.execute,
    run.add_sub_parser: run.execute,
}


def wrap(text, width=120):
    # type: (typing.Text, int) -> typing.Text
    wrapper = TextWrapper(expand_tabs=False, replace_whitespace=False, break_long_words=False, width=width)
    return '\n'.join('\n'.join(wrapper.wrap(line)) for line in text.splitlines())


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

    parser.add_argument(
        '-r', '--rules',
        nargs='+',
        help='Rules to apply for compatibility detection. (default: %(default)s)',
        default=RuleRegistry.rules(),
        choices=RuleRegistry.rules(),
    )

    subparsers = parser.add_subparsers(help='help for sub-command', dest='command')
    for add_sub_command_parser, associated_function in _SUB_COMMAND_ASSOCIATED_FUNCTION_MAPPING.items():
        add_sub_command_parser(subparsers).set_defaults(func=associated_function)

    if not RuleRegistry.rules():
        raise parser.error('No rules are defined.')

    return parser
