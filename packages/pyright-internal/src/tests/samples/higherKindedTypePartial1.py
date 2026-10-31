# This sample tests a type constructor parameter whose bound is a partial
# application: the bound fixes some type arguments and leaves others as
# free type variables that determine the constructor's arity.

from collections import OrderedDict
from typing import Any


# D has arity 1 (only T is free); the value type is fixed to Any.
def keys_of[T, D: dict[T, Any]](mapping: D[T]) -> D[T]:
    return mapping


d1: dict[int, str] = {}
reveal_type(keys_of(d1), expected_text="dict[int, Any]")

od1: OrderedDict[str, float] = OrderedDict()
reveal_type(keys_of(od1), expected_text="OrderedDict[str, Any]")


# A bound that fixes the key type: M has arity 1 over the value type.
def values_of[V, M: dict[str, V]](mapping: M[V]) -> M[V]:
    return mapping


d2: dict[str, int] = {}
reveal_type(values_of(d2), expected_text="dict[str, int]")

# This should generate an error because the key type does not match the
# fixed key type in the bound.
values_of(d1)


# This should generate an error because D has arity 1.
def too_many[T, D: dict[T, Any]](mapping: D[T, T]) -> None: ...
