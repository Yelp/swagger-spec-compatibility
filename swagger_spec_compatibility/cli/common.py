# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import typing  # noqa: F401
from argparse import ArgumentTypeError
from os.path import abspath
from os.path import exists
from os.path import expanduser
from os.path import expandvars
from textwrap import TextWrapper

import typing_extensions
from six.moves.urllib.parse import urljoin
from six.moves.urllib.parse import urlsplit
from six.moves.urllib.request import pathname2url


class CLIProtocol(typing_extensions.Protocol):
    command = None  # type: typing.Text
    func = None  # type: typing.Callable[['CLIProtocol'], int]


def uri(param):
    # type: (str) -> str
    if urlsplit(param).scheme:
        return param

    path = expanduser(expandvars(param))
    if exists(path):
        return urljoin('file:', pathname2url(abspath(path)))

    raise ArgumentTypeError('`{param}` is not an existing file and either a valid URI'.format(param=param))


def wrap(text, width=120, indent=''):
    # type: (typing.Text, int, typing.Text) -> typing.Text
    wrapper = TextWrapper(
        expand_tabs=False,
        replace_whitespace=False,
        break_long_words=False,
        width=width,
        initial_indent=str(indent),
        subsequent_indent=str(indent),
    )
    return '\n'.join('\n'.join(wrapper.wrap(line)) for line in text.splitlines())
