from typing import TypeVar, overload

from . import Array, ChunkedArray, DataType, Scalar

_DataTypeT = TypeVar("_DataTypeT", bound=DataType)


@overload
def cast(arr: Array[Scalar[DataType]], target_type: _DataTypeT) -> Array[Scalar[_DataTypeT]]: ...


@overload
def cast(
    arr: ChunkedArray[Scalar[DataType]], target_type: _DataTypeT
) -> ChunkedArray[Scalar[_DataTypeT]]: ...


def cast(
    arr: Array[Scalar[DataType]] | ChunkedArray[Scalar[DataType]],
    target_type: _DataTypeT,
) -> Array[Scalar[_DataTypeT]] | ChunkedArray[Scalar[_DataTypeT]]:
    raise NotImplementedError