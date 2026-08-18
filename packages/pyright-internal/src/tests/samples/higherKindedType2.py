# This sample tests inference of a unary type constructor from an argument.

from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class Box(Generic[T]):
    pass


class OtherBox(Generic[T]):
    pass


F = TypeVar("F", Box[T], OtherBox[T])


def same_constructor(first: F[int], second: F[str]) -> None:
    pass


same_constructor(Box[int](), Box[str]())

# This should generate an error because the constructors differ.
same_constructor(Box[int](), OtherBox[str]())


def same_constructor_pep695[T_inner, F_pep695: (Box[T_inner], OtherBox[T_inner])](
    first: F_pep695[int], second: F_pep695[str]
) -> None:
    pass


same_constructor_pep695(Box[int](), Box[str]())

# This should generate an error because the constructors differ.
same_constructor_pep695(Box[int](), OtherBox[str]())