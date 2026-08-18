from typing import Generic, TypeVar


class DataType:
    pass


class Int64Type(DataType):
    pass


class StringType(DataType):
    pass


_DataType_co = TypeVar("_DataType_co", bound=DataType, covariant=True)


class Scalar(Generic[_DataType_co]):
    pass


class Int64Scalar(Scalar[Int64Type]):
    pass


_Scalar_co = TypeVar("_Scalar_co", bound=Scalar[DataType], covariant=True)


class Array(Generic[_Scalar_co]):
    pass


class ChunkedArray(Generic[_Scalar_co]):
    pass


def array(values: list[int]) -> Array[Int64Scalar]:
    return Array()


def chunked_array(values: list[list[int]]) -> ChunkedArray[Int64Scalar]:
    return ChunkedArray()


def string() -> StringType:
    return StringType()