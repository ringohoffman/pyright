from __future__ import annotations

from typing import Any, Generic, TypeVar

# Base classes reflecting pyarrow Cython runtime hierarchy
class _Weakrefable:
    pass


class _PandasConvertible(_Weakrefable):
    pass


class DataType(_Weakrefable):
    pass


class Int8Type(DataType):
    pass


class Int16Type(DataType):
    pass


class Int32Type(DataType):
    pass


class Int64Type(DataType):
    pass


class UInt8Type(DataType):
    pass


class UInt16Type(DataType):
    pass


class UInt32Type(DataType):
    pass


class UInt64Type(DataType):
    pass


class FloatType(DataType):
    pass


class DoubleType(DataType):
    pass


class StringType(DataType):
    pass


class BinaryType(DataType):
    pass


class BooleanType(DataType):
    pass


class NullType(DataType):
    pass


class ListType(DataType):
    pass


class LargeListType(DataType):
    pass


class MapType(DataType):
    pass


class StructType(DataType):
    pass


class UnionType(DataType):
    pass


class DictionaryType(DataType):
    pass


_DataType_co = TypeVar("_DataType_co", bound=DataType, covariant=True)



class Scalar(_Weakrefable, Generic[_DataType_co]):
    pass


class NullScalar(Scalar[NullType]):
    pass


class BooleanScalar(Scalar[BooleanType]):
    pass


class Int8Scalar(Scalar[Int8Type]):
    pass


class UInt8Scalar(Scalar[UInt8Type]):
    pass


class Int16Scalar(Scalar[Int16Type]):
    pass


class UInt16Scalar(Scalar[UInt16Type]):
    pass


class Int32Scalar(Scalar[Int32Type]):
    pass


class UInt32Scalar(Scalar[UInt32Type]):
    pass


class Int64Scalar(Scalar[Int64Type]):
    pass


class UInt64Scalar(Scalar[UInt64Type]):
    pass


class HalfFloatScalar(Scalar[FloatType]):
    pass


class FloatScalar(Scalar[FloatType]):
    pass


class DoubleScalar(Scalar[DoubleType]):
    pass


class BinaryScalar(Scalar[BinaryType]):
    pass


class StringScalar(BinaryScalar):
    pass


class FixedSizeBinaryScalar(BinaryScalar):
    pass


class Date32Scalar(Scalar[DataType]):
    pass


class Date64Scalar(Scalar[DataType]):
    pass


class Time32Scalar(Scalar[DataType]):
    pass


class Time64Scalar(Scalar[DataType]):
    pass


class TimestampScalar(Scalar[DataType]):
    pass


class DurationScalar(Scalar[DataType]):
    pass


class MonthDayNanoIntervalScalar(Scalar[DataType]):
    pass


class Decimal128Scalar(Scalar[DataType]):
    pass


class Decimal256Scalar(Scalar[DataType]):
    pass


class ListScalar(Scalar[ListType]):
    pass


class LargeListScalar(ListScalar):
    pass


class MapScalar(ListScalar):
    pass


class StructScalar(Scalar[StructType]):
    pass


class UnionScalar(Scalar[UnionType]):
    pass


class DictionaryScalar(Scalar[DictionaryType]):
    pass


_Scalar_co = TypeVar("_Scalar_co", bound=Scalar[Any], covariant=True)
_ScalarT = TypeVar("_ScalarT", bound=Scalar[Any], covariant=True)


class Array(_PandasConvertible, Generic[_Scalar_co]):
    def __init__(self, array: Any) -> None: ...


class NullArray(Array[NullScalar]):
    pass


class BooleanArray(Array[BooleanScalar]):
    pass


class NumericArray(Array[_ScalarT]):
    pass


class IntegerArray(NumericArray[_ScalarT]):
    pass


class FloatingPointArray(NumericArray[_ScalarT]):
    pass


class Int8Array(IntegerArray[Int8Scalar]):
    pass


class UInt8Array(IntegerArray[UInt8Scalar]):
    pass


class Int16Array(IntegerArray[Int16Scalar]):
    pass


class UInt16Array(IntegerArray[UInt16Scalar]):
    pass


class Int32Array(IntegerArray[Int32Scalar]):
    pass


class UInt32Array(IntegerArray[UInt32Scalar]):
    pass


class Int64Array(IntegerArray[Int64Scalar]):
    pass


class UInt64Array(IntegerArray[UInt64Scalar]):
    pass


class HalfFloatArray(FloatingPointArray[HalfFloatScalar]):
    pass


class FloatArray(FloatingPointArray[FloatScalar]):
    pass


class DoubleArray(FloatingPointArray[DoubleScalar]):
    pass


class BinaryArray(Array[BinaryScalar]):
    pass


class StringArray(Array[StringScalar]):
    pass


class FixedSizeBinaryArray(Array[FixedSizeBinaryScalar]):
    pass


class Decimal32Array(FixedSizeBinaryArray):
    pass


class Decimal64Array(FixedSizeBinaryArray):
    pass


class Decimal128Array(FixedSizeBinaryArray):
    pass


class Decimal256Array(FixedSizeBinaryArray):
    pass


class Date32Array(NumericArray[Date32Scalar]):
    pass


class Date64Array(NumericArray[Date64Scalar]):
    pass


class TimestampArray(NumericArray[TimestampScalar]):
    pass


class Time32Array(NumericArray[Time32Scalar]):
    pass


class Time64Array(NumericArray[Time64Scalar]):
    pass


class DurationArray(NumericArray[DurationScalar]):
    pass


class MonthDayNanoIntervalArray(Array[MonthDayNanoIntervalScalar]):
    pass


class BaseListArray(Array[_ScalarT]):
    pass


class ListArray(BaseListArray[ListScalar]):
    pass


class LargeListArray(BaseListArray[LargeListScalar]):
    pass


class MapArray(ListArray):
    pass


class StructArray(Array[StructScalar]):
    pass


class UnionArray(Array[UnionScalar]):
    pass


class DictionaryArray(Array[DictionaryScalar]):
    pass


class ChunkedArray(_PandasConvertible, Generic[_Scalar_co]):
    pass


def array(values: list[int]) -> Int64Array:
    return Int64Array([])


def chunked_array(values: list[list[int]]) -> ChunkedArray[Int64Scalar]:
    return ChunkedArray()


def int8() -> Int8Type:
    return Int8Type()


def int16() -> Int16Type:
    return Int16Type()


def int32() -> Int32Type:
    return Int32Type()


def int64() -> Int64Type:
    return Int64Type()


def uint8() -> UInt8Type:
    return UInt8Type()


def uint16() -> UInt16Type:
    return UInt16Type()


def uint32() -> UInt32Type:
    return UInt32Type()


def uint64() -> UInt64Type:
    return UInt64Type()


def float32() -> FloatType:
    return FloatType()


def float64() -> DoubleType:
    return DoubleType()


def string() -> StringType:
    return StringType()


def binary() -> BinaryType:
    return BinaryType()


def bool_() -> BooleanType:
    return BooleanType()
