# This sample tests higher-kinded self-type polymorphism on generic mapping classes (bidict pattern).

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import reveal_type


class BidirectionalMapping[KT, VT](Mapping[KT, VT]):
    def __init__(self, mapping: Mapping[KT, VT]) -> None:
        super().__init__()

    def __len__(self) -> int:
        raise NotImplementedError

    def __getitem__(self, key: KT) -> VT:
        raise NotImplementedError

    def __iter__(self) -> Iterator[KT]:
        raise NotImplementedError

    def inverse[MapT: BidirectionalMapping[KT, VT]](self: MapT[KT, VT]) -> MapT[VT, KT]:
        raise NotImplementedError


class bidict[KT, VT](BidirectionalMapping[KT, VT]):
    pass


element_by_atomicnum = bidict({0: "hydrogen", 1: "helium"})
reveal_type(element_by_atomicnum, expected_text="bidict[int, str]")

# Calling inverse() on bidict[int, str] preserves bidict constructor and returns bidict[str, int]
inverted = element_by_atomicnum.inverse()
reveal_type(inverted, expected_text="bidict[str, int]")


# Calling inverse() on base BidirectionalMapping[int, str] returns BidirectionalMapping[str, int]
base_map = BidirectionalMapping({0: "hydrogen", 1: "helium"})
reveal_type(base_map.inverse(), expected_text="BidirectionalMapping[str, int]")
