# This sample specifies that an unconstrained TypeVar is not an HKT constructor
# and must reject subscription.

from __future__ import annotations


# This should generate errors because F is an unconstrained TypeVar and cannot be subscripted.
def identity[F](value: F[int]) -> F[int]:
    raise NotImplementedError
