# This sample specifies when a PEP 695 TypeVar can accept type arguments.

from __future__ import annotations


class Box[T]:
    pass


class OtherBox[T]:
    pass


# A type parameter declared with inner type parameters is a valid constructor.
def accepts_type_arg[Constructor[X]: (Box[X], OtherBox[X])](value: Constructor[int]) -> Constructor[int]:
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
def rejects_mixed_kind[Mixed[X]: (Box[X], OtherBox[X])](value: Mixed, item: Mixed[int]) -> None:
    pass
