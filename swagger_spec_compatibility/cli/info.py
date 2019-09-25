# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import platform

import pkg_resources

from swagger_spec_compatibility.cli.common import add_rule_discovery_argument
from swagger_spec_compatibility.cli.common import cli_rules
from swagger_spec_compatibility.cli.common import CLIProtocol
from swagger_spec_compatibility.rules import RuleRegistry


def execute(cli_args):  # pragma: no cover
    # type: (CLIProtocol) -> int
    print(
        'swagger-spec-compatibility: {swagger_spec_compatibility_version}\n'
        'Python version: {python_implementation} - {python_version}\n'
        'Python compiler: {python_compiler}\n'
        'Discovered rules:\n    {rules}'.format(
            swagger_spec_compatibility_version=pkg_resources.get_distribution('swagger-spec-compatibility').version,
            python_implementation=platform.python_implementation(),
            python_version=platform.python_version(),
            python_compiler=platform.python_compiler(),
            rules='\n    '.join(
                '{rule_name}: {rule.__module__}.{rule.__name__}'.format(rule_name=rule_name, rule=RuleRegistry.rule(rule_name))
                for rule_name in cli_rules()
            ),
        ),
    )

    return 0


def add_sub_parser(subparsers):
    # type: (argparse._SubParsersAction) -> argparse.ArgumentParser
    info_parser = subparsers.add_parser('info', help='Reports tool\'s information')
    add_rule_discovery_argument(info_parser)
    return info_parser
