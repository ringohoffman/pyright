# This sample tests binary constructor variables.

from __future__ import annotations

from typing import Generic, TypeVar, reveal_type

K = TypeVar("K")
V = TypeVar("V")
K2 = TypeVar("K2")
V2 = TypeVar("V2")


class Map(Generic[K, V]):
    pass


class OrderedMap(Generic[K, V]):
    pass


F = TypeVar("F", Map[K, V], OrderedMap[K, V])


def remap(value: F[K, V], key_type: type[K2], value_type: type[V2]) -> F[K2, V2]:
    raise NotImplementedError


mapping = remap(Map[int, str](), str, bytes)
reveal_type(mapping, expected_text="Map[str, bytes]")

ordered = remap(OrderedMap[int, str](), str, bytes)
reveal_type(ordered, expected_text="OrderedMap[str, bytes]")


def remap_pep695[
    K_inner, V_inner, F_pep695: (Map[K_inner, V_inner], OrderedMap[K_inner, V_inner]), K2_inner, V2_inner
](
    value: F_pep695[K_inner, V_inner], key_type: type[K2_inner], value_type: type[V2_inner]
) -> F_pep695[K2_inner, V2_inner]:
    raise NotImplementedError


mapping_pep695 = remap_pep695(Map[int, str](), str, bytes)
reveal_type(mapping_pep695, expected_text="Map[str, bytes]")

ordered_pep695 = remap_pep695(OrderedMap[int, str](), str, bytes)
reveal_type(ordered_pep695, expected_text="OrderedMap[str, bytes]")