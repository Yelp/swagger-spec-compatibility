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

from six.moves.urllib.parse import urljoin
from six.moves.urllib.parse import urlsplit
from six.moves.urllib.request import pathname2url


def uri(param):
    # type: (str) -> str
    if urlsplit(param).scheme:
        return param

    path = expanduser(expandvars(param))
    if exists(path):
        return urljoin('file:', pathname2url(abspath(path)))

    raise ArgumentTypeError('`{param}` is not an existing file and either a valid URI'.format(param=param))


def wrap(text, width=120):
    # type: (typing.Text, int) -> typing.Text
    wrapper = TextWrapper(expand_tabs=False, replace_whitespace=False, break_long_words=False, width=width)
    return '\n'.join('\n'.join(wrapper.wrap(line)) for line in text.splitlines())
