# This sample tests PEP 695 bounds declared by constructor template parameters.

from __future__ import annotations

from typing import reveal_type


class Scalar:
    pass


class IntScalar(Scalar):
    pass


class NotScalar:
    pass


class Array[T]:
    pass


class ChunkedArray[T]:
    pass


def preserve[S: Scalar, F[X: Scalar]: (Array[X], ChunkedArray[X])](value: F[S]) -> F[S]:
    raise NotImplementedError


valid = preserve(Array[IntScalar]())
reveal_type(valid, expected_text="Array[IntScalar]")

# This should generate an error because NotScalar violates the template parameter bound.
preserve(Array[NotScalar]())
