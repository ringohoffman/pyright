# This sample specifies that ordinary applied bounds do not create constructor variables.

from __future__ import annotations


class Array[T]:
    pass


class ChunkedArray[T]:
    pass


# This should generate an error because Bounded is an ordinary TypeVar with an applied bound.
def rejects_applied_bound[Bounded: Array[object] | ChunkedArray[object]](value: Bounded[int]) -> None:
    pass
