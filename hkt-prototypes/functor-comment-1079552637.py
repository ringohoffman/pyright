# https://github.com/python/typing/issues/548#issuecomment-1079552637
#
# Use case from Joel Berkeley (and tek):
# Functor mapping over arbitrary containers while preserving the container constructor.
#
# Without HKT:
# In standard Python (PEP 484 / PEP 695), it is impossible to define a generic `map` method
# on a base class or a universal `fmap` function that transforms element types (A -> B) while
# preserving the concrete container type F:
# - `Self` cannot be re-parameterized to a new element type (e.g. `Self[B]` is illegal).
# - Standard TypeVars are concrete types (kind *), so `F[B]` is illegal.
# Subclasses are forced to re-declare and duplicate the `map` method signature on every subtype,
# or erase the container down to an abstract interface like `Iterable[B]`.
#
# With HKT:
# Base classes and standalone functions can parameterize over type constructors:
# - Method on base class: `def map[B, F[T]: Functor[Any]](self: F[A], f: Callable[[A], B]) -> F[B]`
#   Subclasses inherit the method with zero signature duplication.
# - Standalone `fmap`: captures the higher-kinded container constructor `F[T]` (or `M[K, V]`)
#   and applies the new element type `B`, preserving `list`, `deque`, `set`, `dict`, etc.

from collections import OrderedDict, deque
from collections.abc import Callable, Iterable, Mapping
from typing import Any, Protocol, overload, reveal_type, runtime_checkable


# 1. Base Functor class with inherited .map()
class Functor[A]:
    def map[B, F[T]: Functor[Any]](self: F[A], f: Callable[[A], B]) -> F[B]:
        cls = type(self)
        if isinstance(self, list):
            return cls([f(x) for x in self])  # type: ignore
        raise NotImplementedError


class InheritedList[T](list[T], Functor[T]):
    pass


class SubSpecialList[T](InheritedList[T]):
    pass


# Subclasses inherit .map() without redeclaring it
xs = InheritedList([1, 2, 3])
res_xs = xs.map(str)
reveal_type(res_xs, expected_text="InheritedList[str]")

sub_xs = SubSpecialList([1, 2, 3])
res_sub = sub_xs.map(str)
reveal_type(res_sub, expected_text="SubSpecialList[str]")


# 2. Mappable Protocol for custom duck-typed containers
@runtime_checkable
class Mappable[A](Protocol):
    def map[B, F[T]](self: F[A], f: Callable[[A], B]) -> F[B]:
        ...


class SpecialList[T](list[T]):
    def map[B](self, f: Callable[[T], B]) -> SpecialList[B]:
        return SpecialList([f(x) for x in self])


res = SpecialList([1, 2]).map(str)
reveal_type(res, expected_text="SpecialList[str]")


# 3. Universal standalone fmap function
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
    if isinstance(xs, Mappable):
        return xs.map(f)  # pyright: ignore[reportUnknownMemberType]

    cls = type(xs)  # pyright: ignore[reportUnknownVariableType]
    if isinstance(xs, Mapping):
        return cls((k, f(v)) for k, v in xs.items())  # pyright: ignore[reportUnknownVariableType]

    return cls(f(x) for x in xs)


# Reveal_type assertions across custom and standard containers
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

# Runtime functional validation
assert res_xs == ["1", "2", "3"] and isinstance(res_xs, InheritedList)
assert res_sub == ["1", "2", "3"] and isinstance(res_sub, SubSpecialList)
assert mapped_custom == ["1", "2"] and isinstance(mapped_custom, SpecialList)
assert mapped_list == ["1", "2"] and type(mapped_list) is list
assert mapped_deque == deque(["1", "2"]) and type(mapped_deque) is deque
assert mapped_set == {"1", "2"} and type(mapped_set) is set
assert mapped_frozenset == frozenset({"1", "2"}) and type(mapped_frozenset) is frozenset
assert mapped_dict == {1: "10", 2: "20"} and type(mapped_dict) is dict
assert mapped_ordered_dict == OrderedDict({1: "10", 2: "20"}) and type(mapped_ordered_dict) is OrderedDict
