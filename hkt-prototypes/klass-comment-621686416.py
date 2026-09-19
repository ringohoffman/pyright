# https://github.com/python/typing/issues/548#issuecomment-621686416
#
# Use case from sobolevn (returns / dry-python):
# A generic factory function `create(klass, value)` that accepts a generic class constructor
# (or factory callable) and instantiates it with a value, returning `T[K]` without requiring callers
# to pre-specialize the class or losing the element type.
#
# Without HKT:
# In standard Python (PEP 484 / PEP 695):
#     def create[K, T](klass: Callable[[K], T], value: K) -> T[K]: ...
# fails immediately because `T` is a concrete type (kind *), not a type constructor:
# "Type variable 'T' used with arguments".
# If typed as `klass: Callable[[K], T[K]]` without declaring `T` as higher-kinded, `T` must already
# be applied or concrete. Callers cannot pass unspecialized generic constructors and infer `T` and `K`
# simultaneously. Libraries like `returns` were forced to write custom mypy plugins to emulate HKT.
#
# With HKT:
# `T` is declared as a type constructor `T[X]`:
#     def create[K, T[X]](klass: Callable[[K], T[K]], value: K) -> T[K]:
#         return klass(value)
# Passing `create(Box, "a")` captures `T = Box` and `K = str`, producing `Box[str]`.

from collections.abc import Callable
from typing import reveal_type


class Box[T]:
    def __init__(self, my_value: T, some_kwarg: int | None = None) -> None:
        self.value = my_value


class Container[T]:
    def __init__(self, item: T) -> None:
        self.item = item


def create[K, T[X]](klass: Callable[[K], T[K]], value: K) -> T[K]:
    return klass(value)


# 1. Unspecialized Box + str -> Box[str]
b = create(Box, "a")
reveal_type(b, expected_text="Box[str]")

# 2. Unspecialized Container + int -> Container[int]
c = create(Container, 42)
reveal_type(c, expected_text="Container[int]")

# 3. Runtime functional validation
assert b.value == "a"
assert c.item == 42
