# This sample specifies that bare unparameterized generic origins in TypeVar
# constraints do NOT declare HKT constructors and must reject subscription.

from __future__ import annotations

from typing import Generic, TypeVar

A = TypeVar("A")
B = TypeVar("B")
T_co = TypeVar("T_co", covariant=True)


class Array(Generic[T_co]):
    pass


class ChunkedArray(Generic[T_co]):
    pass


# F is constrained to bare unparameterized Array and ChunkedArray (not explicit templates like Array[T]).
# Therefore, F is an ordinary TypeVar of kind * and cannot be subscripted as F[A].
F = TypeVar("F", Array, ChunkedArray)


# This should generate errors because F is not subscriptable.
def transform(value: F[A], new_value: B) -> F[B]:
    raise NotImplementedError