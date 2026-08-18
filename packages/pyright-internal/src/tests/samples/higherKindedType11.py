# This sample tests bounds declared by constructor template parameters.

from __future__ import annotations

from typing import Generic, TypeVar, reveal_type


class Scalar:
    pass


class IntScalar(Scalar):
    pass


class NotScalar:
    pass


S = TypeVar("S", bound=Scalar)
T = TypeVar("T")


class Array(Generic[T]):
    pass


class ChunkedArray(Generic[T]):
    pass


F = TypeVar("F", Array[S], ChunkedArray[S])


def preserve(value: F[S]) -> F[S]:
    raise NotImplementedError


valid = preserve(Array[IntScalar]())
reveal_type(valid, expected_text="Array[IntScalar]")

# This should generate an error because NotScalar violates the template parameter bound S.
preserve(Array[NotScalar]())