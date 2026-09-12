# https://github.com/python/typing/issues/548#issuecomment-1079552637
from abc import ABC, abstractmethod
from collections import OrderedDict, deque
from collections.abc import Callable, Iterable, Mapping
from typing import Any, Protocol, overload, reveal_type, runtime_checkable

# ==============================================================================
# Joel Berkeley's Exact Definition (from python/typing#548 comment 1079552637)
# ==============================================================================
class Functor[A]:
    def map[B, F[T]: Functor[Any]](self: F[A], f: Callable[[A], B]) -> F[B]:
        # Concrete implementation defined once on the base class:
        cls = type(self)
        if isinstance(self, list):
            return cls([f(x) for x in self])  # type: ignore
        raise NotImplementedError


class InheritedList[T](list[T], Functor[T]):
    pass


class SubSpecialList[T](InheritedList[T]):
    pass


# Subclasses do NOT redefine `map` at all!
xs = InheritedList([1, 2, 3])
res_xs = xs.map(str)
reveal_type(res_xs, expected_text="InheritedList[str]")

sub_xs = SubSpecialList([1, 2, 3])
res_sub = sub_xs.map(str)
reveal_type(res_sub, expected_text="SubSpecialList[str]")


# ==============================================================================
# Extended Pythonic Ecosystem: Protocol + Standalone Universal fmap
# ==============================================================================

# 1. The Protocol for custom objects / types that implement .map()
@runtime_checkable
class Mappable[A](Protocol):
    def map[B, F[T]](self: F[A], f: Callable[[A], B]) -> F[B]:
        ...


class SpecialList[T](list[T]):
    def map[B](self, f: Callable[[T], B]) -> SpecialList[B]:
        return SpecialList([f(x) for x in self])

# Usage is natural object-oriented Python:
res = SpecialList([1, 2]).map(str)  # SpecialList[str]
reveal_type(res, expected_text="SpecialList[str]")

# 2. The Unified Standalone Function (with overloads for both worlds)
@overload
def fmap[A, B, F[T]: Mappable[Any]](f: Callable[[A], B], xs: F[A]) -> F[B]:
    """Prefers the custom .map() method if the container provides one."""
    ...

@overload
def fmap[K, A, B, M[K2, V2]: Mapping[K2, V2]](f: Callable[[A], B], xs: M[K, A]) -> M[K, B]:
    """Maps over values of any Mapping (dict, OrderedDict, etc.), preserving key K and constructor M."""
    ...

@overload
def fmap[A, B, F[T]: Iterable[T]](f: Callable[[A], B], xs: F[A]) -> F[B]:
    """Maps over any Iterable container, preserving constructor F."""
    ...

def fmap(f: Callable[..., Any], xs: Any) -> Any:
    # 1. Check if the object knows how to map itself (Protocol duck-typing)
    if isinstance(xs, Mappable):
        return xs.map(f)

    cls = type(xs)

    # 2. Mappings (preserve keys, map values, construct same type)
    if isinstance(xs, Mapping):
        return cls((k, f(v)) for k, v in xs.items())

    # 3. Iterables (preserve exact runtime type)
    return cls(f(x) for x in xs)


# 3. Validating reveal_type across both custom and standard containers
mapped_custom = fmap(str, SpecialList([1, 2]))
reveal_type(mapped_custom, expected_text="SpecialList[str]")

mapped_list = fmap(str, [1, 2])
reveal_type(mapped_list, expected_text="list[str]")

mapped_deque = fmap(str, deque([1, 2]))
reveal_type(mapped_deque, expected_text="deque[str]")

mapped_set = fmap(str, {1, 2})
reveal_type(mapped_set, expected_text="set[str]")

mapped_frozenset = fmap(str, frozenset({1, 2}))
reveal_type(mapped_frozenset, expected_text="frozenset[str]")

mapped_dict = fmap(str, {1: 10, 2: 20})
reveal_type(mapped_dict, expected_text="dict[int, str]")

mapped_ordered_dict = fmap(str, OrderedDict({1: 10, 2: 20}))
reveal_type(mapped_ordered_dict, expected_text="OrderedDict[int, str]")
