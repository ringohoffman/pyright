"""Minimal higher-kinded type target based on pyarrow.compute.cast."""

from __future__ import annotations

import itertools
from typing import TypeAlias, TypeVar, overload, reveal_type

import pyarrow as pa
import pyarrow.compute as pc

T = TypeVar("T")
_DataTypeT = TypeVar("_DataTypeT", bound=pa.DataType)
_ScalarT = TypeVar("_ScalarT", bound=pa.Scalar[pa.DataType])
_ContainerT = TypeVar(
	"_ContainerT",
	bound=pa.Array[_ScalarT] | pa.ChunkedArray[_ScalarT],
)


ListofList: TypeAlias = list[list[T]]


def flatten(list_of_list: ListofList[T]) -> list[T]:
	return list(itertools.chain.from_iterable(list_of_list))


@overload
def cast_overloaded(
	value: pa.Array[pa.Scalar[pa.DataType]], target_type: _DataTypeT
) -> pa.Array[pa.Scalar[_DataTypeT]]: ...


@overload
def cast_overloaded(
	value: pa.ChunkedArray[pa.Scalar[pa.DataType]], target_type: _DataTypeT
) -> pa.ChunkedArray[pa.Scalar[_DataTypeT]]: ...


def cast_overloaded(
	value: pa.Array[pa.Scalar[pa.DataType]] | pa.ChunkedArray[pa.Scalar[pa.DataType]],
	target_type: _DataTypeT,
) -> pa.Array[pa.Scalar[_DataTypeT]] | pa.ChunkedArray[pa.Scalar[_DataTypeT]]:
	return pc.cast(value, target_type)


def cast_hkt(
	value: _ContainerT[pa.Scalar[pa.DataType]],
	target_type: _DataTypeT,
) -> _ContainerT[pa.Scalar[_DataTypeT]]:
	return pc.cast(value, target_type)

int_array: pa.Array[pa.Int64Scalar] = pa.array([1, 2, 3])
string_array_overloaded = cast_overloaded(int_array, pa.string())
reveal_type(string_array_overloaded, expected_str="Array[Scalar[StringType]]")
string_array_hkt = cast_hkt(int_array, pa.string())
reveal_type(string_array_hkt, expected_str="IntegerArray[Scalar[StringType]]")

int_chunks: pa.ChunkedArray[pa.Int64Scalar] = pa.chunked_array([[1, 2], [3]])
string_chunks_overloaded = cast_overloaded(int_chunks, pa.string())
reveal_type(string_chunks_overloaded, expected_str="ChunkedArray[Scalar[StringType]]")
string_chunks_hkt = cast_hkt(int_chunks, pa.string())
reveal_type(string_chunks_hkt, expected_str="ChunkedArray[Scalar[StringType]]")

int_array = pa.Int64Array([1, 2, 3])
string_array_overloaded = cast_overloaded(int_array, pa.int32())
reveal_type(string_array_overloaded, expected_str="Array[Scalar[Int32Type]]")
string_array_hkt = cast_hkt(int_array, pa.int32())
reveal_type(string_array_hkt, expected_str="IntegerArray[Scalar[Int32Type]]")
