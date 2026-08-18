# This sample tests JAX-style correlation between PyTree leaf packs and callback parameters.

# pyright: reportMissingModuleSource=false

from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping, Sequence
from typing import TypeAlias, TypeVar, TypeVarTuple, reveal_type

from typing_extensions import Map

LeafT = TypeVar("LeafT")
R = TypeVar("R")
LeafTs = TypeVarTuple("LeafTs")
KeyPath: TypeAlias = tuple[Hashable, ...]
PyTree: TypeAlias = Mapping[Hashable, "PyTree[LeafT]"] | Sequence[LeafT] | LeafT


def tree_map_with_path(
    f: Callable[[KeyPath, *LeafTs], R],
    *trees: *Map[PyTree, *LeafTs],
) -> PyTree[R]:
    raise NotImplementedError


def make_int_tree() -> PyTree[int]:
    raise NotImplementedError


def make_str_tree() -> PyTree[str]:
    raise NotImplementedError


int_tree = make_int_tree()
str_tree = make_str_tree()
reveal_type(int_tree, expected_text="Mapping[Hashable, PyTree] | Sequence[int] | int")
reveal_type(str_tree, expected_text="Mapping[Hashable, PyTree] | Sequence[str] | str")

mapped = tree_map_with_path(lambda path, count, text: text * count, int_tree, str_tree)
reveal_type(mapped, expected_text="Mapping[Hashable, PyTree] | Sequence[str] | str")


def tree_map_with_path_pep695[*LeafTs, R](
    f: Callable[[KeyPath, *LeafTs], R],
    *trees: *Map[PyTree, *LeafTs],
) -> PyTree[R]:
    raise NotImplementedError


mapped_pep695 = tree_map_with_path_pep695(lambda path, count, text: text * count, int_tree, str_tree)
reveal_type(mapped_pep695, expected_text="Mapping[Hashable, PyTree] | Sequence[str] | str")