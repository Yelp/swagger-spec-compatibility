# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import typing  # noqa: F401
from argparse import ArgumentTypeError
from os.path import abspath
from os.path import exists
from os.path import expanduser
from os.path import expandvars

import typing_extensions
from six.moves.urllib.parse import urljoin
from six.moves.urllib.parse import urlsplit
from six.moves.urllib.request import pathname2url
from six.moves.urllib.request import url2pathname


class CLIProtocol(typing_extensions.Protocol):
    command = None  # type: typing.Text
    func = None  # type: typing.Callable[['CLIProtocol'], int]


def uri(param):
    # type: (str) -> str
    if urlsplit(param).scheme:
        return param

    path = expanduser(expandvars(url2pathname(param)))
    if exists(path):
        return urljoin('file:', pathname2url(abspath(path)))

    raise ArgumentTypeError('`{param}` is not an existing file and either a valid URI'.format(param=param))
