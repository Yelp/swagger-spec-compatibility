# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing
from abc import abstractmethod
from collections import defaultdict
from itertools import chain

from bravado_core.spec import Spec  # noqa: F401
from six import iteritems
from six import iterkeys
from six import text_type
from six.moves import zip_longest

from swagger_spec_compatibility.cache import typed_lru_cache


T = typing.TypeVar('T')


PathType = typing.Tuple[typing.Union[typing.Text, int], ...]


def format_path(path):
    # type: (PathType) -> typing.Text
    return '#/{}'.format('/'.join(text_type(path_item) for path_item in path))


class Walker(typing.Generic[T]):
    # TODO: add path blacklists to quickly cut descending
    def __init__(self, left, right, **kwargs):
        # type: (typing.Any, typing.Any, typing.Any) -> None
        self.left = left
        self.right = right
        self._inner_walk_calls = defaultdict(list)  # type: typing.DefaultDict[typing.Tuple[int, ...], typing.List[PathType]]
        for attr_name, attr_value in iteritems(kwargs):
            setattr(self, attr_name, attr_value)

    def should_path_be_walked_through(self, path):
        # type: (PathType) -> bool
        return True

    @abstractmethod
    def dict_check(
        self,
        path,  # type: PathType
        left_dict,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
        right_dict,  # type: typing.Optional[typing.Mapping[typing.Text, typing.Any]]
    ):
        # type: (...) -> None  # noqa
        pass

    @abstractmethod
    def list_check(
        self,
        path,  # type: PathType
        left_list,  # type: typing.Optional[typing.Sequence[typing.Any]]
        right_list,  # type: typing.Optional[typing.Sequence[typing.Any]]
    ):
        # type: (...) -> None  # noqa
        pass

    @abstractmethod
    def value_check(
        self,
        path,  # type: PathType
        left_value,  # type: typing.Any
        right_value,  # type: typing.Any
    ):
        # type: (...) -> None
        pass

    def _is_recursive_call(self, path, left, right):
        # type: (PathType, typing.Any, typing.Any) -> bool
        cache_key = (id(left), id(right))

        if cache_key in self._inner_walk_calls and any(
            path[:len(known_path)] == known_path for known_path in self._inner_walk_calls[cache_key]
        ):
            # Deal with recursive objects
            return True

        self._inner_walk_calls[cache_key].append(path)
        return False

    def _inner_walk(self, path, left, right):
        # type: (PathType, typing.Any, typing.Any) -> None

        if not self.should_path_be_walked_through(path) or self._is_recursive_call(path, left, right):
            return

        # TODO: make better walking if the two objects have different type
        if isinstance(left, dict) and isinstance(right, dict):
            self.dict_check(path, left, right)
            for key in set(chain(iterkeys(left), iterkeys(right))):
                self._inner_walk(tuple(chain(path, [key])), left.get(key), right.get(key))

        elif isinstance(left, list) and isinstance(right, list):
            self.list_check(path, left, right)
            for index, (old_item, new_item) in enumerate(zip_longest(left, right)):
                self._inner_walk(tuple(chain(path, [index])), old_item, new_item)
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


class SchemaWalker(Walker[T]):
    def __init__(self, left_spec, right_spec, **kwargs):
        # type: (Spec, Spec, typing.Any) -> None
        super(SchemaWalker, self).__init__(
            left=left_spec.deref_flattened_spec,
            right=right_spec.deref_flattened_spec,
            left_spec=left_spec,
            right_spec=right_spec,
            **kwargs
        )
