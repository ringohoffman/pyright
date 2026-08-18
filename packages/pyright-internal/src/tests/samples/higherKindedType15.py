# This sample specifies that ordinary applied bounds do not create constructor variables.

from __future__ import annotations

from typing import Generic, TypeVar

T_co = TypeVar("T_co", covariant=True)


class Array(Generic[T_co]):
    pass


class ChunkedArray(Generic[T_co]):
    pass


Bounded = TypeVar("Bounded", bound=Array[object] | ChunkedArray[object])


# This should generate an error because Bounded is an ordinary TypeVar with an applied bound.
def rejects_applied_bound(value: Bounded[int]) -> None:
    pass


# This should generate an error for the same reason under PEP 695 syntax.
def rejects_applied_bound_pep695[Bounded: Array[object] | ChunkedArray[object]](value: Bounded[int]) -> None:
    pass