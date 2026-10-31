# This sample tests that constructor inference preserves distinct outer containers.

from __future__ import annotations

from typing import reveal_type


class Array[A]:
    pass


class ChunkedArray[A]:
    pass


def transform[A, B, F[X]: (Array[X], ChunkedArray[X])](value: F[A], target_type: type[B]) -> F[B]:
    raise NotImplementedError


array = transform(Array[int](), str)
reveal_type(array, expected_text="Array[str]")

chunks = transform(ChunkedArray[int](), str)
reveal_type(chunks, expected_text="ChunkedArray[str]")
