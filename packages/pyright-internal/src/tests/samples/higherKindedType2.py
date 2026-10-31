# This sample tests inference of a unary type constructor from an argument.

from __future__ import annotations


class Box[T]:
    pass


class OtherBox[T]:
    pass


def same_constructor[F[X]: (Box[X], OtherBox[X])](first: F[int], second: F[str]) -> None:
    pass


same_constructor(Box[int](), Box[str]())

# This should generate an error because the constructors differ.
same_constructor(Box[int](), OtherBox[str]())
