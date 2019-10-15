# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing

from swagger_spec_compatibility.cli import parser
from swagger_spec_compatibility.cli.common import post_process_rules_cli_arguments
from swagger_spec_compatibility.cli.common import pre_process_cli_to_discover_rules


def main(argv=None):
    # type: (typing.Optional[typing.Sequence[typing.Text]]) -> int
    pre_process_cli_to_discover_rules(argv)
    args = post_process_rules_cli_arguments(parser().parse_args(argv))
    exit_code = args.func(args)  # type: int
    return exit_code


if __name__ == '__main__':
    exit(main())
