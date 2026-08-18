# https://github.com/python/typing/issues/548#issuecomment-621195693
from collections.abc import Iterator, Mapping
from typing import reveal_type


class BidirectionalMapping[KT, VT](Mapping[KT, VT]):
    def __init__(self, mapping: Mapping[KT, VT]) -> None:
          super().__init__()
    def __len__(self) -> int:
            ...
    def __getitem__(self, key: KT) -> VT:
            ...
    def __iter__(self) -> Iterator[KT]:
        ...
    def inverse[MapT: BidirectionalMapping[KT, VT]](self: MapT[KT, VT]) -> MapT[VT, KT]:
        ...


class bidict[KT, VT](BidirectionalMapping[KT, VT]):
    ...


element_by_atomicnum = bidict({0: "hydrogen", 1: "helium"})
reveal_type(element_by_atomicnum, expected_text="bidict[int, str]")

reveal_type(element_by_atomicnum.inverse(), expected_text="bidict[str, int]")
