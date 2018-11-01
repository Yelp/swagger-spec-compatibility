# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import argparse  # noqa: F401
import typing  # noqa: F401

from swagger_spec_compatibility.cli.common import uri


_Namespace = typing.NamedTuple(
    '_Namespace', [
        ('command', typing.Text),
        ('func', typing.Callable[[typing.Iterable[typing.Any]], None]),
        ('rules', typing.Iterable[typing.Text]),
        ('strict', bool),
        ('old_spec', typing.Text),
        ('new_spec', typing.Text),
    ],
)


def execute(args):
    # type: (_Namespace) -> int
    return 1  # TODO(maci) implement logic


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
