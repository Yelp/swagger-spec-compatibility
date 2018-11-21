# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing
from abc import abstractmethod
from itertools import chain
from textwrap import TextWrapper

from six import iteritems
from six import iterkeys
from six import text_type
from six.moves import zip_longest

from swagger_spec_compatibility.cache import typed_lru_cache

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
        return str('{}(old={}, new={})'.format(self.__class__.__name__, self.old, self.new))  # pragma: no cover  # This statement is present only to have a nicer REPL experience # noqa


class Walker(typing.Generic[T]):
    def __init__(self, left, right, **kwargs):
        # type: (typing.Any, typing.Any, typing.Any) -> None
        self.left = left
        self.right = right
        for attr_name, attr_value in iteritems(kwargs):
            setattr(self, attr_name, attr_value)

    @abstractmethod
    def dict_check(
        self,
        path,  # type: typing.Tuple[typing.Text, ...]
        left_dict,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
        right_dict,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
    ):
        # type: (...) -> None  # noqa
        pass

    @abstractmethod
    def list_check(
        self,
        path,  # type: typing.Tuple[typing.Text, ...]
        left_list,  # type: typing.Optional[typing.Sequence[typing.Any]]
        right_list,  # type: typing.Optional[typing.Sequence[typing.Any]]
    ):
        # type: (...) -> None  # noqa
        pass

    @abstractmethod
    def value_check(
        self,
        path,  # type: typing.Tuple[typing.Text, ...]
        left_value,  # type: typing.Any
        right_value,  # type: typing.Any
    ):
        # type: (...) -> None
        pass

    def _inner_walk(self, path, left, right):
        # type: (typing.Tuple[typing.Text, ...], typing.Any, typing.Any) -> None
        if isinstance(left, dict) and isinstance(right, dict):
            self.dict_check(path, left, right)
            for key in set(chain(iterkeys(left), iterkeys(right))):
                self._inner_walk(tuple(chain(path, [key])), left.get(key), right.get(key))

        elif isinstance(left, list) and isinstance(right, list):
            self.list_check(path, left, right)
            for index, (old_item, new_item) in enumerate(zip_longest(left, right)):
                self._inner_walk(tuple(chain(path, [text_type(index)])), left, new_item)
        else:
            self.value_check(path, left, right)

    @abstractmethod
    def walk_response(self):
        # type: () -> typing.Iterable[T]
        pass

    @typed_lru_cache(maxsize=1)
    def walk(self):
        # type: () -> typing.Iterable[T]
        self._inner_walk(
            path=tuple(),
            left=self.left,
            right=self.right,
        )
        return self.walk_response()
