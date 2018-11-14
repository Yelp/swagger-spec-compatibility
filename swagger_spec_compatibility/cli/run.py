# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import argparse  # noqa: F401
import typing  # noqa: F401

from swagger_spec_compatibility.cli.common import CLIProtocol
from swagger_spec_compatibility.cli.common import uri
from swagger_spec_compatibility.rules import compatibility_status
from swagger_spec_compatibility.rules import RuleRegistry
from swagger_spec_compatibility.spec_utils import load_spec_from_uri


class _Namespace(CLIProtocol):
    rules = None  # type: typing.Iterable[typing.Text]
    strict = None  # type: bool
    old_spec = None  # type: typing.Text
    new_spec = None  # type: typing.Text


def execute(args):
    # type: (_Namespace) -> int
    rules_to_check = {RuleRegistry.rule(rule_name): rule_name for rule_name in args.rules}

    rules_to_error_level_mapping = compatibility_status(
        old_spec=load_spec_from_uri(args.old_spec),
        new_spec=load_spec_from_uri(args.new_spec),
        rules=rules_to_check.keys(),
        strict=args.strict,
    )

    rules_to_error_level_mapping = {  # Remove rules that did not have errors
        rule: error_level
        for rule, error_level in rules_to_error_level_mapping.items()
        if error_level
    }

    if rules_to_error_level_mapping:
        print('Failed rules: {}'.format(', '.join(rules_to_check[r] for r in rules_to_error_level_mapping)))

    return 1 if rules_to_error_level_mapping else 0


def add_sub_parser(subparsers):
    # type: (argparse._SubParsersAction) -> argparse.ArgumentParser
    run_detection_parser = subparsers.add_parser('run', help='run backward compatibility detection')
    run_detection_parser.add_argument(
        '--strict',
        action='store_true',
        help='Convert warnings to errors',
    )
    run_detection_parser.add_argument(
        'old_spec',
        type=uri,
        help='Path/URI of the "old" version of the Swagger spec',
    )
    run_detection_parser.add_argument(
        'new_spec',
        type=uri,
        help='Path/URI of the "new" version of the Swagger spec',
    )
    return run_detection_parser
