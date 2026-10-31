# This sample tests that a constructor variable has consistent arity.

from __future__ import annotations


class Box[T]:
    pass


class OtherBox[T]:
    pass


# This should generate an error because F has arity 1 but is applied to two type arguments.
def inconsistent[F[X]: (Box[X], OtherBox[X])](first: F[int], second: F[int, str]) -> None:
    pass
