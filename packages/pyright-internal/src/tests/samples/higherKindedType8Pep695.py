# This sample specifies that concrete-applied bounds/constraints in PEP 695
# do NOT declare HKT constructors and must reject subscription.

from __future__ import annotations

from typing import Any


class Array[T]:
    pass


class ChunkedArray[T]:
    pass


# F is constrained to concrete specialized types Array[Any] and ChunkedArray[Any].
# Because these lack free template TypeVars, F is an ordinary TypeVar and rejects subscription.
def transform[F: (Array[Any], ChunkedArray[Any]), A, B](value: F[A], new_value_type: type[B]) -> F[B]:
    raise NotImplementedError


def transform_type[F: (Array[Any], ChunkedArray[Any]), A, B](
    array_type: type[F[A]], new_value_type: type[B]
) -> type[F[B]]:
    raise NotImplementedError
