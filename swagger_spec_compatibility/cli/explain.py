# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import argparse  # noqa: F401
import typing  # noqa: F401


def execute(args):
    # type: (typing.Any) -> None
    raise NotImplementedError


def add_sub_parser(subparsers):
    # type: (argparse._SubParsersAction) -> argparse.ArgumentParser
    return subparsers.add_parser('explain', help='explain selected rules')
