# This sample tests reapplication of a solved constructor with a new type argument.

from __future__ import annotations

from typing import reveal_type


class Box[A]:
    pass


def transform[A, B, F[X]: Box[X]](value: F[A], new_value: B) -> F[B]:
    raise NotImplementedError


box = transform(Box[int](), "value")
reveal_type(box, expected_text="Box[str]")
