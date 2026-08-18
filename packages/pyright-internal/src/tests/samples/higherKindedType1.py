# This sample specifies that an unconstrained TypeVar is not an HKT constructor
# and must reject subscription.

from __future__ import annotations

from typing import TypeVar

F = TypeVar("F")


# This should generate errors because F is an unconstrained TypeVar and cannot be subscripted.
def identity(value: F[int]) -> F[int]:
    raise NotImplementedError


# This should generate errors for the same reason under PEP 695 syntax.
def identity_pep695[F](value: F[int]) -> F[int]:
    raise NotImplementedError