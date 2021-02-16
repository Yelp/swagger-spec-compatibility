# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing
import warnings
from abc import abstractmethod
from itertools import chain

from bravado_core.spec import Spec
from six import iteritems
from six import iterkeys
from six import text_type
from six.moves import zip_longest


class NoValue(object):
    pass


# HTTP verbs as described by https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#parameterObject
_HTTP_OPERATIONS = {'get', 'put', 'post', 'delete', 'options', 'head', 'patch'}
T = typing.TypeVar('T')
PathType = typing.Tuple[typing.Union[typing.Text, int], ...]
NO_VALUE = NoValue()


def format_path(path):
    # type: (PathType) -> typing.Text
    return '#/{}'.format('/'.join(text_type(path_item) for path_item in path))


class Walker(typing.Generic[T]):
    """
    Generic Walker over two objects.

    The abstract class strips away the details related to dictionary vs list iterations,
    path update etc.
    """

    def __init__(self, left, right, **kwargs):
        # type: (typing.Any, typing.Any, typing.Any) -> None
        self.left = left
        self.right = right
        self._walk_result = NO_VALUE  # type: typing.Union[NoValue, typing.Iterable[T]]
        self._inner_walk_calls = {}  # type: typing.Dict
        for attr_name, attr_value in iteritems(kwargs):
            setattr(self, attr_name, attr_value)

    def should_path_be_walked_through(self, path):
        # type: (PathType) -> bool
        """
        Determine whether to traverse or interrupt traversal of a given path.

        This method allows Walkers to skip traversal of area of the specs that are "not interesting".
        This will allow to write simpler methods and to avoid needless traversing of the Specs.
        """
        return True

    @abstractmethod
    def dict_check(
        self,
        path,  # type: PathType
        left_dict,  # type: typing.Union[typing.Mapping[typing.Text, typing.Any], NoValue]
        right_dict,  # type: typing.Union[typing.Mapping[typing.Text, typing.Any], NoValue]
    ):
        # type: (...) -> typing.Iterable[T]
        """
        Compare the left and right content of path in case both objects are dictionaries.
        """
        raise NotImplementedError()

    @abstractmethod
    def list_check(
        self,
        path,  # type: PathType
        left_list,  # type: typing.Union[typing.Sequence[typing.Any], NoValue]
        right_list,  # type: typing.Union[typing.Sequence[typing.Any], NoValue]
    ):
        # type: (...) -> typing.Iterable[T]
        """
        Compare the left and right content of path in case both objects are list.
        """
        raise NotImplementedError()

    @abstractmethod
    def value_check(
        self,
        path,  # type: PathType
        left_value,  # type: typing.Any
        right_value,  # type: typing.Any
    ):
        # type: (...) -> typing.Iterable[T]
        """
        Compare the left and right content of path in case the objects have different types or are not dictionaries or lists.
        """
        raise NotImplementedError()

    def _is_recursive_call(self, path, left, right):
        # type: (PathType, typing.Any, typing.Any) -> bool
        """
        Determine if the current objects are already been traversed.

        Swagger specification could contain recursive definitions and references.
        Due to the fact that we fully dereference the specs then there will be no
        good way to know if we've already visited the given objects other than
        using their ids.
        """
        # This function is called a _lot_ on large Swagger specs and requires
        # some optimization to avoid 20+ minute check times.
        #
        # The idea is to check if we have ever walked the same (left, right)
        # nodes when exploring a parent path. If so, this part of the spec tree
        # is recursive and already explored, and we can stop walking.
        #
        # The below implementation stores each path component in a tree
        # structure, e.g.
        #    {(id_left, id_right): {'paths': {'/foo': {'post': True}}}}
        #
        # Recursing down the tree and looking for `True` is logically
        # equivalent to looking for matching prefixes for the cache key, but
        # much faster.
        cache_path = (id(left), id(right)) + path
        cur = self._inner_walk_calls
        for path_component in cache_path:
            prev = cur
            cur = cur.setdefault(path_component, {})
            if cur is True:
                return True
        else:
            prev[path_component] = True
            return False

    def _inner_walk(self, path, left, right):
        # type: (PathType, typing.Any, typing.Any) -> typing.Iterable[T]
        """
        Fully traverse the left and right objects.

        The traversal will short-circuit in case:
         * a given path should not be traversed
         * the path has already been traversed (recursive definition)
        """
        if not self.should_path_be_walked_through(path) or self._is_recursive_call(path, left, right):
            return ()

        if isinstance(left, dict) and isinstance(right, dict):
            return chain(
                self.dict_check(path, left, right),
                (
                    value
                    for key in set(chain(iterkeys(left), iterkeys(right)))
                    for value in self._inner_walk(
                        path=tuple(chain(path, [key])),
                        left=left.get(key, NO_VALUE),
                        right=right.get(key, NO_VALUE),
                    )
                ),
            )
        elif isinstance(left, list) and isinstance(right, list):
            return chain(
                self.list_check(path, left, right),
                (
                    value
                    for index, (left_item, right_item) in enumerate(zip_longest(left, right, fillvalue=NO_VALUE))
                    for value in self._inner_walk(
                        path=tuple(chain(path, [index])),
                        left=left_item,
                        right=right_item,
                    )
                ),
            )
        else:
            return self.value_check(path, left, right)

    def walk(self):
        # type: () -> typing.Iterable[T]
        """
        Fully traverse the left and right objects.
        NOTE:   the traversing is internally cached such that all the subsequent calls
                to `walk()` are equivalent to an attribute access
        """
        if isinstance(self._walk_result, NoValue):  # pragma: no branch
            self._walk_result = list(
                self._inner_walk(
                    path=tuple(),
                    left=self.left,
                    right=self.right,
                ),
            )
        return self._walk_result


class SchemaWalker(Walker[T]):
    """
    Walker aware of how a Swagger schema looks like.

    The main difference between this walker and Walker is that this walker
    keeps in consideration some peculiarity of the swagger specs.

    The walker implementation should never worry about dereferencing as the traversing
    is performed on the fully flattened and dereferenced specs
    """

    def __init__(self, left_spec, right_spec, **kwargs):
        # type: (Spec, Spec, typing.Any) -> None
        super(SchemaWalker, self).__init__(
            left=left_spec.deref_flattened_spec,
            right=right_spec.deref_flattened_spec,
            left_spec=left_spec,
            right_spec=right_spec,
            **kwargs
        )

    def _is_path_a_parameter_list_location(self, path):
        # type: (PathType) -> bool
        """
        Check if the given path is compatible with a path that contains the list of
        parameters of an operation object.

        The possible locations are:
        1) /paths/<endpoint path>/parameters
            https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#path-item-object
        2) /paths/<endpoint path>/<http verb>/parameters
            https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#operation-object
        """
        if len(path) == 3 and path[0] == 'paths' and path[2] == 'parameters':
            return True
        elif len(path) == 4 and path[0] == 'paths' and path[2] in _HTTP_OPERATIONS and path[3] == 'parameters':
            return True

        return False

    def _get_original_parameter_path(self, path, parameters_index):
        # type: (PathType, typing.Mapping[typing.Text, int]) -> PathType
        try:
            # Ignoring type as path[-1] could be an integer which is not expected for parameters_index
            # it's not really a big deal as it should not happen and if this happens then KeyError will be thrown
            return tuple(chain(path[:-1], [parameters_index[path[-1]]]))  # type: ignore
        except KeyError:
            # This could happen only if the parameter was present only on the old specs
            # or if the path was actually not "modified" by the walker (NOTE: the later condition should not be possible)
            # but let's do it so mypy is happy too
            return path

    def fix_parameter_path(self, path, original_path, value):
        # type: (PathType, PathType, T) -> T
        """
        Fix an eventual path present on the value returned by the walker.

        The SwaggerAwareWalker modifies the indexing approach used for parameters due to the fact
        that parameters are defined as arrays and modifying their order would not change the semantic.
        """
        try:
            # ignoring type as we're exploiting duck typing and is not easy to validate the protocol at run time
            return value.fix_parameter_path(path=path, original_path=original_path)  # type: ignore
        except TypeError as type_error:
            warnings.warn(
                str(
                    'Unexpected {}.fix_parameter_path signature. {}'.format(
                        value.__class__.__name__,
                        type_error,
                    ),
                ),
                category=RuntimeWarning,
            )
        except AttributeError:
            # Ignore such exception as it means that value does not implement fix_parameter_path method
            pass

        return value

    def _inner_walk(self, path, left, right):
        # type: (PathType, typing.Any, typing.Any) -> typing.Iterable[T]

        if self._is_path_a_parameter_list_location(path):
            left_parameters_map = {} if left is NO_VALUE else {parameter['name']: parameter for parameter in left}
            right_parameters_map = {} if right is NO_VALUE else {parameter['name']: parameter for parameter in right}
            parameters_index = {} if right is NO_VALUE else {parameter['name']: index for index, parameter in enumerate(right)}
            return (
                self.fix_parameter_path(
                    path=new_path,
                    original_path=self._get_original_parameter_path(new_path, parameters_index),
                    value=value,
                )
                for key in set(chain(iterkeys(left_parameters_map), iterkeys(right_parameters_map)))
                for new_path in (tuple(chain(path, [key])),)  # Small trick to allow variable definition in generator-comprehension
                for value in self._inner_walk(
                    path=tuple(chain(path, [key])),
                    left=left_parameters_map.get(key, NO_VALUE),
                    right=right_parameters_map.get(key, NO_VALUE),
                )
            )
        else:
            return super(SchemaWalker, self)._inner_walk(path=path, left=left, right=right)
