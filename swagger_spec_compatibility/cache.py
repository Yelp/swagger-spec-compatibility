# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing

try:
    from functools import lru_cache as _lru_cache  # type: ignore # py>=3.2
except ImportError:  # pragma: no cover
    from functools32 import lru_cache as _lru_cache  # py<3.2


T = typing.TypeVar('T')


class typed_lru_cache(object):

    __slots__ = ('maxsize', 'uncached_function', 'cached_function')

    def __init__(self, maxsize=None):
        # type: (typing.Optional[int]) -> None
        assert isinstance(maxsize, (int, type(None)))
        self.maxsize = maxsize  # type: typing.Optional[int]
        self.uncached_function = None  # type: typing.Optional[typing.Any]
        self.cached_function = None  # type: typing.Optional[typing.Any]

    def __call__(self, fn):
        # type: (T) -> T
        # assert (self.cached_function is not None) == (self.uncached_function is not None)

        if self.cached_function is None:
            self.uncached_function = fn  # type: T
            self.cached_function = _lru_cache(maxsize=self.maxsize)(fn)
        else:
            assert self.uncached_function == fn  # pragma: no cover  # defensive approach, this should not happen

        return typing.cast(T, self.cached_function)
