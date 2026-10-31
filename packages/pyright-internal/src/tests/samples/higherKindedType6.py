# This sample tests the nested generic structure used by pyarrow.compute.cast.

from __future__ import annotations

from typing import reveal_type


class DataType:
    pass


class Int64Type(DataType):
    pass


class StringType(DataType):
    pass


class Scalar[DataTypeT_co: DataType]:
    pass


class Int64Scalar(Scalar[Int64Type]):
    pass


class Array[ScalarT_co: Scalar[DataType]]:
    pass


class ChunkedArray[ScalarT_co: Scalar[DataType]]:
    pass


def cast[
    ContainerT[D: DataType]: (Array[Scalar[D]], ChunkedArray[Scalar[D]]), NewDataTypeT: DataType
](value: ContainerT[DataType], target_type: NewDataTypeT) -> ContainerT[NewDataTypeT]:
    raise NotImplementedError


array = cast(Array[Int64Scalar](), StringType())
reveal_type(array, expected_text="Array[Scalar[StringType]]")

chunks = cast(ChunkedArray[Int64Scalar](), StringType())
reveal_type(chunks, expected_text="ChunkedArray[Scalar[StringType]]")
