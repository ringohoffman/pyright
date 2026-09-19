# Context: scipy-stubs/sparse/_base.pyi (lines 806-866)
# Reference: https://github.com/jorenham/hkt-survey/blob/main/scipy_sparse_astype.md
#
# Use case from SciPy:
# `scipy.sparse._spbase.astype()` casts the scalar element type of a sparse array/matrix
# while preserving the concrete sparse subclass (`bsr_array`, `csr_array`, etc.).
#
# Crucially, SciPy sparse subclasses have HETEROGENEOUS ARITIES:
# - Binary subclasses (like `csr_array[ScalarT, ShapeT]`): leave shape generic (* -> * -> *)
# - Unary subclasses (like `bsr_array[ScalarT]` via `bsr_base`): pin shape to `tuple[int, int]` (* -> *)
#
# Without HKT:
# Today `scipy-stubs` is forced to maintain 14 per-subclass overloads, plus a `Self`-typed
# "same dtype" overload.
# `Self` does NOT solve this: `astype` changes the scalar parameter, so the return type is
# not `Self`, but "the same constructor as `self`, specialized with the new scalar type".
#
# With HKT:
# Subclasses inherit constructor-polymorphic `astype` definitions matching their arity:
# 1. Binary constructors (`_spbase`):
#    `def astype[NewScalar, Array[S, Sh: tuple[int, ...]]: _spbase[S, Sh]](self: Array[ScalarT, ShapeT], dtype: type[NewScalar]) -> Array[NewScalar, ShapeT]: ...`
# 2. Unary constructors (`bsr_base`):
#    `def astype[NewScalar, Array[S]: bsr_base[S]](self: Array[ScalarT], dtype: type[NewScalar]) -> Array[NewScalar]: ...`
# Each subclass branch preserves both its concrete constructor and any specialized attributes.

from typing import Any, overload, reveal_type


class _spbase[ScalarT, ShapeT: tuple[int, ...]]:
    def __init__(self, shape: ShapeT, data: list[ScalarT]) -> None:
        self.shape = shape
        self.data = data

    # Binary constructor overload (csr_array, csc_array, coo_array, etc.)
    @overload
    def astype[NewScalar, Array[S, Sh: tuple[int, ...]]: _spbase[S, Sh]](
        self: Array[ScalarT, ShapeT],
        dtype: type[NewScalar],
    ) -> Array[NewScalar, ShapeT]:
        ...

    @overload
    def astype(self, dtype: type[Any]) -> Any:
        ...

    def astype(self, dtype: type[Any]) -> Any:
        cls = type(self)
        converted_data = [dtype(x) for x in self.data]
        return cls(self.shape, converted_data)


# Base class for unary subclasses where ShapeT is pre-bound to tuple[int, int]
class bsr_base[ScalarT](_spbase[ScalarT, tuple[int, int]]):
    # Unary constructor overload (bsr_array, etc.)
    @overload
    def astype[NewScalar, Array[S]: bsr_base[S]](
        self: Array[ScalarT],
        dtype: type[NewScalar],
    ) -> Array[NewScalar]:
        ...

    @overload
    def astype(self, dtype: type[Any]) -> Any:
        ...

    def astype(self, dtype: type[Any]) -> Any:
        cls = type(self)
        converted_data = [dtype(x) for x in self.data]
        return cls(self.shape, converted_data)


class bsr_array[ScalarT](bsr_base[ScalarT]):
    def block_format(self) -> str:
        return "BSR block structure"


class csr_array[ScalarT, ShapeT: tuple[int, ...]](_spbase[ScalarT, ShapeT]):
    def compressed_indices(self) -> list[int]:
        return [0, len(self.data)]


float64 = float
int32 = int

# Test 1: astype on unary subclass bsr_array
bsr: bsr_array[float64] = bsr_array((2, 2), [1.0, 2.0, 3.0, 4.0])
bsr_int = bsr.astype(int32)
reveal_type(bsr_int, expected_text="bsr_array[int]")
assert isinstance(bsr_int, bsr_array)
assert bsr_int.block_format() == "BSR block structure"
assert bsr_int.data == [1, 2, 3, 4]

# Test 2: astype on binary subclass csr_array
type Matrix2D = tuple[int, int]
csr: csr_array[float64, Matrix2D] = csr_array((2, 2), [1.5, 2.5])
csr_int = csr.astype(int32)
reveal_type(csr_int, expected_text="csr_array[int, tuple[int, int]]")
assert isinstance(csr_int, csr_array)
assert csr_int.compressed_indices() == [0, 2]
assert csr_int.data == [1, 2]
