# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from swagger_spec_compatibility.cache import typed_lru_cache

_NUMBER_OF_CALLS = 0


def _foo(number):
    global _NUMBER_OF_CALLS
    _NUMBER_OF_CALLS += 1
    return _NUMBER_OF_CALLS


def test_typed_lru_cache_wraps_results():
    @typed_lru_cache(maxsize=2)
    def foo(number):
        return _foo(number)

    assert foo(1) == 1  # Cache sets number=1 call result
    assert foo(1) == 1  # Cache already knows number=1 call result
    assert foo(2) == 2  # Cache sets number=2 call result
    assert foo(2) == 2  # Cache already knows number=2 call result
    assert foo(3) == 3  # Cache sets number=3 call result and drops number=1 (due to maxsize=2)
    assert foo(3) == 3  # Cache already knows number=3 call result
    assert foo(1) == 4  # Cache does not know anymore the number=1 call result, so sets number=1 call result and drop number=2 (due to maxsize=2)  # noqa
