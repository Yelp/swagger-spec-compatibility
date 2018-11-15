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


def typed_lru_cache(f, maxsize=2):
    # type: (T, int) -> T
    wrapper = _lru_cache(maxsize)(f)  # type: T
    return wrapper
