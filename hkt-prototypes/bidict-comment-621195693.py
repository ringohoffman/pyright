# https://github.com/python/typing/issues/548#issuecomment-621195693
from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping, MutableMapping
from typing import Any, cast, reveal_type


class BidirectionalMapping[KT, VT](Mapping[KT, VT], ABC):
    """Abstract base mapping defining the HKT inverse signature once for the entire hierarchy."""

    @abstractmethod
    def __getitem__(self, key: KT) -> VT: ...

    @abstractmethod
    def __iter__(self) -> Iterator[KT]: ...

    @abstractmethod
    def __len__(self) -> int: ...

    def inverse[MapT: BidirectionalMapping[KT, VT]](self: MapT[KT, VT]) -> MapT[VT, KT]:
        """HKT self-type constructor polymorphism:
        Preserves whatever bidirectional mapping subclass MapT is (e.g. bidict, orderedbidict),
        returning MapT[VT, KT] with inverted type parameters.
        """
        inv: Any = object.__new__(type(self))
        inv._fwdm = getattr(self, "_invm", {})
        inv._invm = getattr(self, "_fwdm", {})
        return cast(MapT[VT, KT], inv)


class bidict[KT, VT](BidirectionalMapping[KT, VT], MutableMapping[KT, VT]):
    """Mutable bidirectional mapping maintaining a 1-to-1 bijection with paired dicts."""

    def __init__(self, mapping: Mapping[KT, VT] | None = None) -> None:
        self._fwdm: dict[KT, VT] = dict(mapping) if mapping is not None else {}
        self._invm: dict[VT, KT] = {v: k for k, v in self._fwdm.items()}

    def __len__(self) -> int:
        return len(self._fwdm)

    def __getitem__(self, key: KT) -> VT:
        return self._fwdm[key]

    def __iter__(self) -> Iterator[KT]:
        return iter(self._fwdm)

    def __setitem__(self, key: KT, val: VT) -> None:
        if key in self._fwdm:
            del self._invm[self._fwdm[key]]
        if val in self._invm:
            del self._fwdm[self._invm[val]]
        self._fwdm[key] = val
        self._invm[val] = key

    def __delitem__(self, key: KT) -> None:
        val = self._fwdm.pop(key)
        del self._invm[val]


class orderedbidict[KT, VT](bidict[KT, VT]):
    pass


# 1. bidict preserves the bidict constructor
element_by_atomicnum = bidict({0: "hydrogen", 1: "helium"})
reveal_type(element_by_atomicnum, expected_text="bidict[int, str]")

inv_elements = element_by_atomicnum.inverse()
reveal_type(inv_elements, expected_text="bidict[str, int]")

# 2. orderedbidict preserves the orderedbidict constructor without any method overrides
ordered = orderedbidict({0: "hydrogen", 1: "helium"})
reveal_type(ordered, expected_text="orderedbidict[int, str]")

inv_ordered = ordered.inverse()
reveal_type(inv_ordered, expected_text="orderedbidict[str, int]")
