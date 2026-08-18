# This sample tests PEP 695 applied-template constraints.

from __future__ import annotations

from typing import reveal_type


class DataType:
    pass


class IntType(DataType):
    pass


class StringType(DataType):
    pass


class Scalar[D: DataType]:
    pass


class IntScalar(Scalar[IntType]):
    pass


class Array[S: Scalar[DataType]]:
    pass


class ChunkedArray[S: Scalar[DataType]]:
    pass


def cast[D: DataType, F: (Array[Scalar[D]], ChunkedArray[Scalar[D]]), B: DataType](
    value: F[DataType], target_type: type[B]
) -> F[B]:
    raise NotImplementedError


array = cast(Array[IntScalar](), StringType)
reveal_type(array, expected_text="Array[Scalar[StringType]]")

chunks = cast(ChunkedArray[IntScalar](), StringType)
reveal_type(chunks, expected_text="ChunkedArray[Scalar[StringType]]")