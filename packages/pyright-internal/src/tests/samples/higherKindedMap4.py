# This sample tests arbitrary-arity zip over iterable element types.

# pyright: reportMissingModuleSource=false

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TypeVarTuple, reveal_type

from typing_extensions import Map

ElementTs = TypeVarTuple("ElementTs")


def zip_iterables(*iterables: *Map[Iterable, *ElementTs]) -> Iterator[tuple[*ElementTs]]:
    raise NotImplementedError


one = zip_iterables([1, 2])
reveal_type(one, expected_text="Iterator[tuple[int]]")

two = zip_iterables([1, 2], ("a", "b"))
reveal_type(two, expected_text="Iterator[tuple[int, str]]")

three = zip_iterables([1, 2], ("a", "b"), {b"x", b"y"})
reveal_type(three, expected_text="Iterator[tuple[int, str, bytes]]")


def zip_iterables_pep695[*ElementTs](
    *iterables: *Map[Iterable, *ElementTs],
) -> Iterator[tuple[*ElementTs]]:
    raise NotImplementedError


three_pep695 = zip_iterables_pep695([1, 2], ("a", "b"), {b"x", b"y"})
reveal_type(three_pep695, expected_text="Iterator[tuple[int, str, bytes]]")