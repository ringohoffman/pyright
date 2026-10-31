# This sample tests binary constructor variables.

from __future__ import annotations

from typing import reveal_type


class Map[K, V]:
    pass


class OrderedMap[K, V]:
    pass


def remap[K, V, K2, V2, F[X, Y]: (Map[X, Y], OrderedMap[X, Y])](
    value: F[K, V], key_type: type[K2], value_type: type[V2]
) -> F[K2, V2]:
    raise NotImplementedError


mapping = remap(Map[int, str](), str, bytes)
reveal_type(mapping, expected_text="Map[str, bytes]")

ordered = remap(OrderedMap[int, str](), str, bytes)
reveal_type(ordered, expected_text="OrderedMap[str, bytes]")
