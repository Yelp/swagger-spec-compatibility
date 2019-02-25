# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401

from swagger_spec_compatibility.cli import parser


def main(argv=None):
    # type: (typing.Optional[typing.Sequence[typing.Text]]) -> int
    args = parser().parse_args(argv)
    exit_code = args.func(args)  # type: int
    return exit_code


if __name__ == '__main__':
    exit(main())
