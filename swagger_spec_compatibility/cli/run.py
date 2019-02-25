# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse  # noqa: F401
import json
import sys
import typing  # noqa: F401

from six import iteritems

from swagger_spec_compatibility.cli.common import CLIProtocol
from swagger_spec_compatibility.cli.common import rules
from swagger_spec_compatibility.cli.common import uri
from swagger_spec_compatibility.rules import compatibility_status
from swagger_spec_compatibility.rules import ValidationMessage  # noqa: F401
from swagger_spec_compatibility.rules.common import BaseRule  # noqa: F401
from swagger_spec_compatibility.rules.common import Level
from swagger_spec_compatibility.rules.common import RuleProtocol  # noqa: F401
from swagger_spec_compatibility.spec_utils import load_spec_from_uri


class _Namespace(CLIProtocol):
    rules = None  # type: typing.Iterable[typing.Text]
    strict = None  # type: bool
    json_output = None  # type: bool
    old_spec = None  # type: typing.Text
    new_spec = None  # type: typing.Text


def _extract_rules_with_given_message_level(
    rules_to_messages_mapping,  # type: typing.Mapping[typing.Type[RuleProtocol], typing.Iterable[ValidationMessage]]
    level,  # type: Level
):
    # type: (...) -> typing.List[ValidationMessage]
    return [
        message
        for rule, messages in iteritems(rules_to_messages_mapping)
        for message in messages
        if message.level is level
    ]


def _print_raw_messages(messages_by_level):
    # type: (typing.Mapping[Level, typing.Iterable[ValidationMessage]]) -> None
    for level, messages in iteritems(messages_by_level):
        messages = list(messages)
        if messages:
            print(
                '{} rules:\n\t{}'.format(
                    level.name,
                    '\n\t'.join(
                        message.string_representation()
                        for message in messages
                    ),
                ),
            )


def _print_json_messages(messages_by_level):
    # type: (typing.Mapping[Level, typing.Iterable[ValidationMessage]]) -> None
    json_output = {}
    for level, messages in iteritems(messages_by_level):
        level_output = [
            message.json_representation()
            for message in messages
        ]
        if level_output:
            json_output[level.name] = level_output
    json.dump(json_output, sys.stdout)


def execute(cli_args):
    # type: (_Namespace) -> int
    rules_to_messages_mapping = compatibility_status(
        old_spec=load_spec_from_uri(cli_args.old_spec),
        new_spec=load_spec_from_uri(cli_args.new_spec),
        rules=rules(cli_args),
    )

    messages_by_level = {
        level: _extract_rules_with_given_message_level(rules_to_messages_mapping, level)
        for level in Level
    }

    if cli_args.json_output:
        _print_json_messages(messages_by_level)
    else:
        _print_raw_messages(messages_by_level)

    if cli_args.strict:
        return 1 if any(messages_by_level.values()) else 0
    else:
        return 1 if any(messages_by_level[Level.ERROR]) else 0


def add_sub_parser(subparsers):
    # type: (argparse._SubParsersAction) -> argparse.ArgumentParser
    run_detection_parser = subparsers.add_parser('run', help='run backward compatibility detection')
    run_detection_parser.add_argument(
        '--strict',
        action='store_true',
        help='Convert warnings to errors',
    )
    run_detection_parser.add_argument(
        '--json-output',
        action='store_true',
        help='Return machine readable json output',
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
