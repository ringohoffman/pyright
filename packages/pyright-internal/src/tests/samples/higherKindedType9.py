# This sample specifies when a TypeVar can accept type arguments.

from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class Box(Generic[T]):
    pass


class OtherBox(Generic[T]):
    pass


# A TypeVar declared with explicit templates is a valid constructor.
LegacyConstructor = TypeVar("LegacyConstructor", Box[T], OtherBox[T])


def accepts_type_arg(value: LegacyConstructor[int]) -> LegacyConstructor[int]:
    raise NotImplementedError


# An unconstrained TypeVar is not a constructor and rejects subscription.
LegacyUnconstrained = TypeVar("LegacyUnconstrained")


# This should generate an error.
def rejects_unconstrained(value: LegacyUnconstrained[int]) -> None:
    pass


# A TypeVar constrained to concrete, non-generic types is not a constructor.
LegacyConcrete = TypeVar("LegacyConcrete", int, str)


# This should generate an error.
def rejects_concrete_constraint(value: LegacyConcrete[int], fallback: LegacyConcrete) -> LegacyConcrete:
    return fallback


# A TypeVar bounded by a concrete, non-generic type is not a constructor.
LegacyBound = TypeVar("LegacyBound", bound=int)


# This should generate an error.
def rejects_concrete_bound(value: LegacyBound[int], fallback: LegacyBound) -> LegacyBound:
    return fallback


# A TypeVar cannot be both an ordinary type and a constructor in one scope.
LegacyMixed = TypeVar("LegacyMixed", Box[T], OtherBox[T])


# This should generate an error.
def rejects_mixed_kind(value: LegacyMixed, item: LegacyMixed[int]) -> None:
    pass