# https://github.com/python/typing/issues/548#issuecomment-970287830
#
# Use case from harahu (and xkortex):
# Typed version of `toolz.dicttoolz.valmap` that transforms mapping values (V -> MappedV)
# while preserving key types K and the target mapping constructor MapT (defaulting to dict).
#
# Without HKT:
# In standard Python (PEP 484 / PEP 695):
#     def valmap(
#         func: Callable[[V], M],
#         d: Mapping[K, V],
#         factory: type[MutableMapping[K, M]] = dict,
#     ) -> MutableMapping[K, M]: ...
# 1. The return type is erased down to the abstract interface `MutableMapping[K, M]`,
#    losing the concrete type even when passing `factory=OrderedDict` or `dict`.
# 2. Writing `factory: type[F] = dict -> F[K, M]` fails because F is an ordinary TypeVar
#    (kind *), not a type constructor: "Type variable 'F' used with arguments".
# Library authors were forced to accept type erasure on return values or generate
# repetitive stub overloads for each concrete mapping class.
#
# With HKT:
# `MapT` is declared as a binary type constructor with an upper bound:
#     def valmap[K, V, MappedV, MapT[_K, _V]: MutableMapping[_K, _V]](
#         func: Callable[[V], MappedV],
#         d: Mapping[K, V],
#         factory: type[MapT[K, MappedV]] = dict,
#     ) -> MapT[K, MappedV]:
#         ...
# - Calling `valmap(str, fib)` infers `dict[int, str]` via constructor default `= dict`.
# - Calling `valmap(str, fib, OrderedDict)` preserves `OrderedDict[int, str]`.

from collections import OrderedDict
from collections.abc import Callable, Mapping, MutableMapping
from typing import reveal_type


def valmap[K, V, MappedV, MapT[_K, _V]: MutableMapping[_K, _V]](
    func: Callable[[V], MappedV],
    d: Mapping[K, V],
    factory: type[MapT[K, MappedV]] = dict,
) -> MapT[K, MappedV]:
    rv = factory()
    rv.update(zip(d.keys(), map(func, d.values())))
    return rv


fib = {1: 2, 2: 3, 3: 5, 5: 8}

# 1. Default factory -> dict[int, str]
res_dict = valmap(str, fib)
reveal_type(res_dict, expected_text="dict[int, str]")

# 2. Explicit OrderedDict factory -> OrderedDict[int, str]
res_ordered = valmap(str, fib, OrderedDict)
reveal_type(res_ordered, expected_text="OrderedDict[int, str]")

# 3. Runtime functional validation
assert res_dict == {1: "2", 2: "3", 3: "5", 5: "8"}
assert isinstance(res_dict, dict)

assert res_ordered == OrderedDict([(1, "2"), (2, "3"), (3, "5"), (5, "8")])
assert isinstance(res_ordered, OrderedDict)
