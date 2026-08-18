# This sample is the canonical Arrow-shaped acceptance specification.

from __future__ import annotations

from typing import Generic, TypeVar, overload, reveal_type


class DataType:
    pass


class IntType(DataType):
    pass


class StringType(DataType):
    pass


D_co = TypeVar("D_co", bound=DataType, covariant=True)


class Scalar(Generic[D_co]):
    pass


class IntScalar(Scalar[IntType]):
    pass


S_co = TypeVar("S_co", bound=Scalar[DataType], covariant=True)


class Array(Generic[S_co]):
    pass


class ChunkedArray(Generic[S_co]):
    pass


D = TypeVar("D", bound=DataType)
B = TypeVar("B", bound=DataType)
F = TypeVar("F", Array[Scalar[D]], ChunkedArray[Scalar[D]])


@overload
def cast(value: Array[Scalar[DataType]], target_type: type[B]) -> Array[Scalar[B]]: ...


@overload
def cast(value: ChunkedArray[Scalar[DataType]], target_type: type[B]) -> ChunkedArray[Scalar[B]]: ...


def cast(
    value: Array[Scalar[DataType]] | ChunkedArray[Scalar[DataType]], target_type: type[B]
) -> Array[Scalar[B]] | ChunkedArray[Scalar[B]]:
    raise NotImplementedError


def cast_hkt(value: F[DataType], target_type: type[B]) -> F[B]:
    return cast(value, target_type)


array = cast_hkt(Array[IntScalar](), StringType)
reveal_type(array, expected_text="Array[Scalar[StringType]]")

chunks = cast_hkt(ChunkedArray[IntScalar](), StringType)
reveal_type(chunks, expected_text="ChunkedArray[Scalar[StringType]]")


def cast_hkt_pep695[D: DataType, F: (Array[Scalar[D]], ChunkedArray[Scalar[D]]), B: DataType](
    value: F[DataType], target_type: type[B]
) -> F[B]:
    return cast(value, target_type)


array_pep695 = cast_hkt_pep695(Array[IntScalar](), StringType)
reveal_type(array_pep695, expected_text="Array[Scalar[StringType]]")

chunks_pep695 = cast_hkt_pep695(ChunkedArray[IntScalar](), StringType)
reveal_type(chunks_pep695, expected_text="ChunkedArray[Scalar[StringType]]")