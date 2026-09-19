# Context: numpy/__init__.pyi (lines 3951-3952)
# Reference: https://github.com/jorenham/hkt-survey/blob/main/numpy_ndarray_view.md
#
# Use case from NumPy:
# `ndarray.view()` returns a new view of array data. It can:
# 1. Preserve the current array class while changing dtype: `arr.view(dtype=np.float32)`
# 2. Transmute to a subclass while preserving shape and dtype: `arr.view(type=MaskedArray)`
# 3. Change both subclass and dtype simultaneously: `arr.view(dtype=np.int32, type=MaskedArray)`
#
# Without HKT:
# In standard Python, NumPy's stubs cannot express transmuting to an unapplied subclass constructor
# `ArrayT` while preserving the current instance's `ShapeT` and `DTypeT`.
# Stubs are forced to type `view(type=...) -> ndarray[Any, Any]`, causing type erasure and false-positive
# errors whenever users access subclass-specific attributes (such as `MaskedArray.mask`).
#
# With HKT:
# The `view` method binds the target class as an unapplied binary constructor `ArrayT[S, D]: ndarray[S, D]`:
#     def view[ArrayT[S, D]: ndarray[S, D]](
#         self: ndarray[ShapeT, DTypeT],
#         type: type[ArrayT],
#     ) -> ArrayT[ShapeT, DTypeT]: ...
# - The target constructor `ArrayT` is captured from `type=MaskedArray`.
# - `ShapeT` and `DTypeT` are transferred from `self`.
# - Return type is specialized to `MaskedArray[tuple[int], int8]`, preserving `.mask`.

from typing import Any, overload, reveal_type


class dtype[Scalar]:
    def __init__(self, scalar_type: type[Scalar]) -> None:
        self.scalar_type = scalar_type


int8 = int
float64 = float


class ndarray[ShapeT: tuple[int, ...], DTypeT]:
    def __init__(self, shape: ShapeT, dt: dtype[DTypeT]) -> None:
        self.shape = shape
        self.dtype = dt

    # Overload 1: Change dtype only, keep same array class constructor
    @overload
    def view[NewDType, SelfT[S: tuple[int, ...], D]: ndarray[S, D]](
        self: SelfT[ShapeT, DTypeT],
        *,
        dtype: dtype[NewDType],
    ) -> SelfT[ShapeT, NewDType]:
        ...

    # Overload 2: Change array subclass constructor, keep same shape and dtype
    @overload
    def view[ArrayT[S: tuple[int, ...], D]: ndarray[S, D]](
        self,
        *,
        type: type[ArrayT],
    ) -> ArrayT[ShapeT, DTypeT]:
        ...

    # Overload 3: Change both array subclass constructor and dtype
    @overload
    def view[NewDType, ArrayT[S: tuple[int, ...], D]: ndarray[S, D]](
        self,
        *,
        dtype: dtype[NewDType],
        type: type[ArrayT],
    ) -> ArrayT[ShapeT, NewDType]:
        ...

    def view(self, *, dtype: Any = None, type: Any = None) -> Any:
        target_cls = type if type is not None else builtins_type(self)
        target_dt = dtype if dtype is not None else self.dtype
        instance = target_cls(self.shape, target_dt)
        return instance


builtins_type = type


class MaskedArray[ShapeT: tuple[int, ...], DTypeT](ndarray[ShapeT, DTypeT]):
    def __init__(self, shape: ShapeT, dt: dtype[DTypeT]) -> None:
        super().__init__(shape, dt)
        self.mask: list[bool] = [False]


# 1. Base vector of int8 with shape tuple[Literal[10]]
vec_i8 = ndarray((10,), dtype(int8))
reveal_type(vec_i8, expected_text="ndarray[tuple[Literal[10]], int]")

# 2. Transmute to MaskedArray: preserves shape (tuple[Literal[10]]) and dtype (int)
vec_masked = vec_i8.view(type=MaskedArray)
reveal_type(vec_masked, expected_text="MaskedArray[tuple[Literal[10]], int]")
assert isinstance(vec_masked, MaskedArray)
assert vec_masked.mask == [False]  # Subclass attribute preserved!

# 3. Change dtype only: preserves base array constructor
vec_f64 = vec_i8.view(dtype=dtype(float64))
reveal_type(vec_f64, expected_text="ndarray[tuple[Literal[10]], float]")
assert isinstance(vec_f64, ndarray)
assert vec_f64.dtype.scalar_type is float64

# 4. Change both constructor and dtype simultaneously:
vec_masked_f64 = vec_i8.view(dtype=dtype(float64), type=MaskedArray)
reveal_type(vec_masked_f64, expected_text="MaskedArray[tuple[Literal[10]], float]")
assert isinstance(vec_masked_f64, MaskedArray)
assert vec_masked_f64.mask == [False]
assert vec_masked_f64.dtype.scalar_type is float64
