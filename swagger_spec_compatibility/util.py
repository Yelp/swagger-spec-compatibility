# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing
from textwrap import TextWrapper

from swagger_spec_compatibility.walkers import PathType  # noqa: F401

T = typing.TypeVar('T')


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


class EntityMapping(typing.Generic[T]):
    __slots__ = ('_old', '_new')

    def __init__(self, old, new):
        # type: (T, T) -> None
        self._old = old
        self._new = new

    @property  # Property needed as temporary workaround to generic named tuples (https://github.com/python/mypy/issues/685)
    def old(self):
        # type: () -> T
        return self._old

    @property  # Property needed as temporary workaround to generic named tuples (https://github.com/python/mypy/issues/685)
    def new(self):
        # type: () -> T
        return self._new

    def __iter__(self):
        # type: () -> typing.Generator[T, None, None]
        yield self.old
        yield self.new

    def __hash__(self):
        # type: () -> int
        return hash((hash(self._old), hash(self._new)))

    def __eq__(self, other):
        # type: (typing.Any) -> bool
        return isinstance(other, self.__class__) and self._old == other._old and self._new == other._new

    def __repr__(self):
        # type: () -> str
        return str('{}(old={}, new={})'.format(
            self.__class__.__name__, self.old,
            self.new,
        ))  # pragma: no cover  # This statement is present only to have a nicer REPL experience # noqa


def is_path_in_top_level_paths(top_level_paths, path):
    # type: (typing.Iterable[PathType], PathType) -> bool
    return any(
        path[:len(acceptable_path)] == acceptable_path
        for acceptable_path in top_level_paths
    )
