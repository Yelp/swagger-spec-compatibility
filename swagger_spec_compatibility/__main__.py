# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import typing  # noqa: F401

from swagger_spec_compatibility.cli import parser


def main(argv=None):
    # type: (typing.Optional[typing.Sequence[typing.Text]]) -> int
    args = parser().parse_args(argv)
    print(args)
    return 0


if __name__ == '__main__':
    exit(main())
