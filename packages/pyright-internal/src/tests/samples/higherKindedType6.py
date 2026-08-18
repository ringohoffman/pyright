# This sample tests the nested generic structure used by pyarrow.compute.cast.

from __future__ import annotations

from typing import Generic, TypeVar, reveal_type


class DataType:
    pass


class Int64Type(DataType):
    pass


class StringType(DataType):
    pass


DataTypeT_co = TypeVar("DataTypeT_co", bound=DataType, covariant=True)


class Scalar(Generic[DataTypeT_co]):
    pass


class Int64Scalar(Scalar[Int64Type]):
    pass


ScalarT_co = TypeVar("ScalarT_co", bound=Scalar[DataType], covariant=True)


class Array(Generic[ScalarT_co]):
    pass


class ChunkedArray(Generic[ScalarT_co]):
    pass


D = TypeVar("D", bound=DataType)
NewDataTypeT = TypeVar("NewDataTypeT", bound=DataType)
ContainerT = TypeVar("ContainerT", Array[Scalar[D]], ChunkedArray[Scalar[D]])


def cast(value: ContainerT[DataType], target_type: NewDataTypeT) -> ContainerT[NewDataTypeT]:
    raise NotImplementedError

array = cast(Array[Int64Scalar](), StringType())
reveal_type(array, expected_text="Array[Scalar[StringType]]")

chunks = cast(ChunkedArray[Int64Scalar](), StringType())
reveal_type(chunks, expected_text="ChunkedArray[Scalar[StringType]]")


def cast_pep695[D_inner: DataType, ContainerT_pep695: (Array[Scalar[D_inner]], ChunkedArray[Scalar[D_inner]]), NewDataTypeT_pep695: DataType](
    value: ContainerT_pep695[DataType], target_type: NewDataTypeT_pep695
) -> ContainerT_pep695[NewDataTypeT_pep695]:
    raise NotImplementedError


array_pep695 = cast_pep695(Array[Int64Scalar](), StringType())
reveal_type(array_pep695, expected_text="Array[Scalar[StringType]]")

chunks_pep695 = cast_pep695(ChunkedArray[Int64Scalar](), StringType())
reveal_type(chunks_pep695, expected_text="ChunkedArray[Scalar[StringType]]")