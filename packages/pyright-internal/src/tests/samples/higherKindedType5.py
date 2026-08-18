# This sample tests that a constructor variable has consistent arity.

from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class Box(Generic[T]):
    pass


class OtherBox(Generic[T]):
    pass


F = TypeVar("F", Box[T], OtherBox[T])


def inconsistent(first: F[int], second: F[int, str]) -> None:
    pass


def inconsistent_pep695[T_inner, F_pep695: (Box[T_inner], OtherBox[T_inner])](
    first: F_pep695[int], second: F_pep695[int, str]
) -> None:
    pass