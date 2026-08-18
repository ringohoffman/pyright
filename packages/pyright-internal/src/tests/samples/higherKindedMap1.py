# This sample tests unary elementwise mapping of a constructor over a type pack.

# pyright: reportMissingModuleSource=false

from __future__ import annotations

from typing import TypeVarTuple, reveal_type

from typing_extensions import Map

Ts = TypeVarTuple("Ts")


def wrap_lists(*values: *Ts) -> tuple[*Map[list, *Ts]]:
    raise NotImplementedError


wrapped = wrap_lists(1, "text", b"bytes")
reveal_type(wrapped, expected_text="tuple[list[int], list[str], list[bytes]]")


def wrap_lists_pep695[*Ts](*values: *Ts) -> tuple[*Map[list, *Ts]]:
    raise NotImplementedError


wrapped_pep695 = wrap_lists_pep695(1, "text", b"bytes")
reveal_type(wrapped_pep695, expected_text="tuple[list[int], list[str], list[bytes]]")