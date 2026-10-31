# This sample tests unconstrained / unbound Higher-Kinded Type (HKT) variables.

from __future__ import annotations

from collections.abc import Callable
from typing import reveal_type


# 1. Function-level unconstrained 1-arity HKT
def fmap[A, B, F[T]](f: Callable[[A], B], xs: F[A]) -> F[B]:
    raise NotImplementedError


class SpecialList[T](list[T]):
    pass


class Box[T]:
    def __init__(self, value: T) -> None:
        self.value = value


# Valid applications to built-in and user-defined 1-param generic constructors
res_list = fmap(str, [1, 2, 3])
reveal_type(res_list, expected_text="list[str]")

res_set = fmap(int, {"1", "2", "3"})
reveal_type(res_set, expected_text="set[int]")

res_special = fmap(str, SpecialList([1, 2, 3]))
reveal_type(res_special, expected_text="SpecialList[str]")

res_box = fmap(str, Box(42))
reveal_type(res_box, expected_text="Box[str]")

# Error: bytearray is not a generic constructor
res_bytearray = fmap(str, bytearray([1, 2]))

# Error: dict has arity 2, not 1
res_dict_err = fmap(str, {1: "a"})


# 2. Function-level unconstrained 2-arity HKT
def bimap[K1, V1, K2, V2, M[K, V]](
    fk: Callable[[K1], K2], fv: Callable[[V1], V2], xs: M[K1, V1]
) -> M[K2, V2]:
    raise NotImplementedError


class Pair[A, B]:
    def __init__(self, first: A, second: B) -> None:
        self.first = first
        self.second = second


res_dict = bimap(str, int, {1: "10", 2: "20"})
reveal_type(res_dict, expected_text="dict[str, int]")

res_pair = bimap(str, bool, Pair(1, 0))
reveal_type(res_pair, expected_text="Pair[str, bool]")

# Error: list has arity 1, not 2
res_list_err = bimap(str, int, [1, 2, 3])


# 3. Class-level unconstrained HKT parameter
class Mapper[F[T]]:
    def map[A, B](self, f: Callable[[A], B], xs: F[A]) -> F[B]:
        raise NotImplementedError


list_mapper = Mapper[list]()
reveal_type(list_mapper.map(str, [1, 2]), expected_text="list[str]")

box_mapper = Mapper[Box]()
reveal_type(box_mapper.map(float, Box(10)), expected_text="Box[float]")

# Error: int is not a generic constructor
int_mapper = Mapper[int]()

# Error: dict has arity 2, not 1
dict_mapper = Mapper[dict]()
