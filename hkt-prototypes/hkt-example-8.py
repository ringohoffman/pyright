# This sample tests PEP 695 constraints over generic constructor origins.

from __future__ import annotations

from typing import Any, reveal_type


class Array[T]:
    pass


class ChunkedArray[T]:
    pass


class Other[T]:
    pass


def transform[F: (Array[Any], ChunkedArray[Any]), A, B](value: F[A], new_value_type: type[B]) -> F[B]:
    raise NotImplementedError

def transform_type[F: (Array[Any], ChunkedArray[Any]), A, B](array_type: type[F[A]], new_value_type: type[B]) -> type[F[B]]:
    raise NotImplementedError


array = transform(Array[int](), str)
reveal_type(array, expected_text="Array[str]")

chunks = transform(ChunkedArray[int](), str)
reveal_type(chunks, expected_text="ChunkedArray[str]")

reveal_type(ChunkedArray[int], expected_text="type[ChunkedArray[int]]")
chunk_type = transform_type(ChunkedArray[int], str)
reveal_type(chunk_type, expected_text="type[ChunkedArray[str]]")

# This should generate an error because Other is not one of F's constraints.
transform(Other[int](), str)
