# This sample tests reapplication of a solved constructor with a new type argument.

from __future__ import annotations

from typing import Generic, TypeVar, reveal_type

A = TypeVar("A")
B = TypeVar("B")


class Box(Generic[A]):
    pass


F = TypeVar("F", bound=Box[A])


def transform(value: F[A], new_value: B) -> F[B]:
    raise NotImplementedError


box = transform(Box[int](), "value")
reveal_type(box, expected_text="Box[str]")


def transform_pep695[A_inner, F_pep695: Box[A_inner], B_inner](
    value: F_pep695[A_inner], new_value: B_inner
) -> F_pep695[B_inner]:
    raise NotImplementedError


box_pep695 = transform_pep695(Box[int](), "value")
reveal_type(box_pep695, expected_text="Box[str]")
