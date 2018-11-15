# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401
from enum import Enum
from textwrap import TextWrapper


class StringEnum(str, Enum):
    """Enum where members are also (and must be) strings"""


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
