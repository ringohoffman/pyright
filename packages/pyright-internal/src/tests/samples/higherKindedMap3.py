# This sample tests positional transpose across an arbitrary pack of tuple rows.

# pyright: reportMissingModuleSource=false

from __future__ import annotations

from typing import TypeVarTuple, reveal_type

from typing_extensions import Map

Rows = TypeVarTuple("Rows")


def transpose_types(*rows: *Rows) -> tuple[*Map[tuple, *Rows]]:
    raise NotImplementedError


one = transpose_types((1, "left"))
reveal_type(one, expected_text="tuple[tuple[int], tuple[str]]")

two = transpose_types((1, "left"), (b"right", 2.0))
reveal_type(two, expected_text="tuple[tuple[int, bytes], tuple[str, float]]")

three = transpose_types((1, "left"), (b"right", 2.0), (True, 3j))
reveal_type(three, expected_text="tuple[tuple[int, bytes, bool], tuple[str, float, complex]]")


def transpose_types_pep695[*Rows](*rows: *Rows) -> tuple[*Map[tuple, *Rows]]:
    raise NotImplementedError


three_pep695 = transpose_types_pep695((1, "left"), (b"right", 2.0), (True, 3j))
reveal_type(three_pep695, expected_text="tuple[tuple[int, bytes, bool], tuple[str, float, complex]]")


# This should generate an error because mapped packs must have equal length.
transpose_types((1,), ("one", "two"))

# This should generate an error for the same reason under PEP 695 syntax.
transpose_types_pep695((1,), ("one", "two"))