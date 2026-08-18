# This sample tests that constructor inference preserves distinct outer containers.

from __future__ import annotations

from typing import Generic, TypeVar, reveal_type

A = TypeVar("A")
B = TypeVar("B")


class Array(Generic[A]):
    pass


class ChunkedArray(Generic[A]):
    pass


F = TypeVar("F", Array[A], ChunkedArray[A])


def transform(value: F[A], target_type: type[B]) -> F[B]:
    raise NotImplementedError


array = transform(Array[int](), str)
reveal_type(array, expected_text="Array[str]")

chunks = transform(ChunkedArray[int](), str)
reveal_type(chunks, expected_text="ChunkedArray[str]")


def transform_pep695[A_inner, F_pep695: (Array[A_inner], ChunkedArray[A_inner]), B_inner](
    value: F_pep695[A_inner], target_type: type[B_inner]
) -> F_pep695[B_inner]:
    raise NotImplementedError


array_pep695 = transform_pep695(Array[int](), str)
reveal_type(array_pep695, expected_text="Array[str]")

chunks_pep695 = transform_pep695(ChunkedArray[int](), str)
reveal_type(chunks_pep695, expected_text="ChunkedArray[str]")