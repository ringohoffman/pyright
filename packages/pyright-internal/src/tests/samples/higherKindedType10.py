# This sample tests legacy applied-template constraints.

from __future__ import annotations

from typing import Generic, TypeVar, reveal_type


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
D = TypeVar("D", bound=DataType)


class Array(Generic[S_co]):
    pass


class ChunkedArray(Generic[S_co]):
    pass


ArrayT = TypeVar("ArrayT", Array[Scalar[D]], ChunkedArray[Scalar[D]])
B = TypeVar("B", bound=DataType)


def cast(value: ArrayT[DataType], target_type: type[B]) -> ArrayT[B]:
    raise NotImplementedError


array = cast(Array[IntScalar](), StringType)
reveal_type(array, expected_text="Array[Scalar[StringType]]")

chunks = cast(ChunkedArray[IntScalar](), StringType)
reveal_type(chunks, expected_text="ChunkedArray[Scalar[StringType]]")