# This sample specifies when a PEP 695 TypeVar can accept type arguments.

from __future__ import annotations


class Box[T]:
    pass


class OtherBox[T]:
    pass


# A TypeVar declared with explicit templates is a valid constructor.
def accepts_type_arg[T, Constructor: (Box[T], OtherBox[T])](value: Constructor[int]) -> Constructor[int]:
    raise NotImplementedError


# An unconstrained TypeVar is not a constructor and rejects subscription.
# This should generate an error.
def rejects_unconstrained[Unconstrained](value: Unconstrained[int]) -> None:
    pass


# A TypeVar constrained to concrete, non-generic types is not a constructor.
# This should generate an error.
def rejects_concrete_constraint[Concrete: (int, str)](value: Concrete[int], fallback: Concrete) -> Concrete:
    return fallback


# A TypeVar bounded by a concrete, non-generic type is not a constructor.
# This should generate an error.
def rejects_concrete_bound[Bound: int](value: Bound[int], fallback: Bound) -> Bound:
    return fallback


# A TypeVar cannot be both an ordinary type and a constructor in one scope.
# This should generate an error.
def rejects_mixed_kind[Mixed[T]: (Box[T], OtherBox[T])](value: Mixed, item: Mixed[int]) -> None:
    pass

def f(box: Box) -> None:
    ...

# Type of parameter "box" is partially unknown
#   Parameter type is "Box[Unknown]"
# Expected type arguments for generic class "Box"
