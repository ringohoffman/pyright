# This sample is the canonical Arrow-shaped acceptance specification.

from __future__ import annotations

from typing import overload, reveal_type


class DataType:
    pass


class IntType(DataType):
    pass


class StringType(DataType):
    pass


class Scalar[D_co: DataType]:
    pass


class IntScalar(Scalar[IntType]):
    pass


class Array[S_co: Scalar[DataType]]:
    pass


class ChunkedArray[S_co: Scalar[DataType]]:
    pass


@overload
def cast[B: DataType](value: Array[Scalar[DataType]], target_type: type[B]) -> Array[Scalar[B]]: ...


@overload
def cast[B: DataType](value: ChunkedArray[Scalar[DataType]], target_type: type[B]) -> ChunkedArray[Scalar[B]]: ...


def cast[B: DataType](
    value: Array[Scalar[DataType]] | ChunkedArray[Scalar[DataType]], target_type: type[B]
) -> Array[Scalar[B]] | ChunkedArray[Scalar[B]]:
    raise NotImplementedError


def cast_hkt[F[D: DataType]: (Array[Scalar[D]], ChunkedArray[Scalar[D]]), B: DataType](
    value: F[DataType], target_type: type[B]
) -> F[B]:
    return cast(value, target_type)


array = cast_hkt(Array[IntScalar](), StringType)
reveal_type(array, expected_text="Array[Scalar[StringType]]")

chunks = cast_hkt(ChunkedArray[IntScalar](), StringType)
reveal_type(chunks, expected_text="ChunkedArray[Scalar[StringType]]")
