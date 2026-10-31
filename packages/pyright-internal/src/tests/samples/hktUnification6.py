# This sample tests casting fixed-type subclasses through higher-kinded
# container templates (e.g. Int32Array -> Array[Int64Dtype]).

from __future__ import annotations

from typing import reveal_type


class DataType:
    pass


class Int32Dtype(DataType):
    pass


class Int64Dtype(DataType):
    pass


# Generic container family
class Array[D: DataType]:
    pass


class ChunkedArray[D: DataType]:
    pass


# Fixed-dtype concrete subclasses (0 type parameters)
class Int32Array(Array[Int32Dtype]):
    pass


class Int32ChunkedArray(ChunkedArray[Int32Dtype]):
    pass


class Unrelated:
    pass


# Higher-kinded transformation preserving container shape (Array vs ChunkedArray)
# while converting the underlying DataType to Int64Dtype.
def to_int64[D: DataType, F[X: DataType]: (Array[X], ChunkedArray[X])](
    array: F[D],
) -> F[Int64Dtype]:
    raise NotImplementedError


# 1. Passing Int32Array (derives from Array[Int32Dtype]) matches F = Array, D = Int32Dtype
# and returns Array[Int64Dtype].
arr = to_int64(Int32Array())
reveal_type(arr, expected_text="Array[Int64Dtype]")

# 2. Passing Int32ChunkedArray (derives from ChunkedArray[Int32Dtype]) matches F = ChunkedArray, D = Int32Dtype
# and returns ChunkedArray[Int64Dtype].
chunks = to_int64(Int32ChunkedArray())
reveal_type(chunks, expected_text="ChunkedArray[Int64Dtype]")

# 3. Unrelated class is rejected
# This should generate an error because Unrelated does not derive from Array or ChunkedArray.
to_int64(Unrelated())
