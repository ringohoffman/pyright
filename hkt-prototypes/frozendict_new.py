from collections.abc import Iterable, Iterator, Mapping
from typing import Any, Protocol, overload, reveal_type

class SupportsKeysAndGetItem[_KT, _VT_co](Protocol):
    def keys(self) -> Iterable[_KT]: ...
    def __getitem__(self, key: _KT, /) -> _VT_co: ...


class frozendict[_KT, _VT](Mapping[_KT, _VT]):
    @overload
    def __new__[KT=Any, VT=Any, SelfT: frozendict[KT, VT] = frozendict[Any, Any]](  # kinda sketchy
        cls: type[SelfT[KT, VT]],
        /,
    ) -> SelfT[KT, VT]: ...
    @overload
    def __new__[VT, SelfT: frozendict[str, VT]](
        cls: type[SelfT[VT]],
        /,
        **kwargs: VT,
    ) -> SelfT[VT]: ...
    @overload
    def __new__[KT, VT, SelfT: frozendict[KT, VT]](
        cls: type[SelfT[KT, VT]],
        map: SupportsKeysAndGetItem[KT, VT],
        /,
    ) -> SelfT[KT, VT]: ...
    @overload
    def __new__[KT, VT, SelfT: frozendict[KT, VT]](
        cls: type[SelfT[KT, VT]],
        iterable: Iterable[tuple[KT, VT]],
        /,
    ) -> SelfT[KT, VT]: ...
    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        ...

    def copy(self) -> frozendict[_KT, _VT]: ...
    def __len__(self) -> int: ...
    def __getitem__(self, key: _KT, /) -> _VT: ...
    def __reversed__(self) -> Iterator[_KT]: ...
    def __iter__(self) -> Iterator[_KT]: ...
    def __hash__(self) -> int: ...


def get_tuple_of_ints() -> list[tuple[int, int]]:
    return [(1, 2), (3, 4)]

reveal_type(frozendict(), expected_text="frozendict[Any, Any]")
reveal_type(frozendict(baz=1), expected_text="frozendict[str, int]")
reveal_type(frozendict({"foo": "bar"}), expected_text="frozendict[str, str]")
reveal_type(frozendict(get_tuple_of_ints()), expected_text="frozendict[int, int]")


class MyFrozendict[KT, VT](frozendict[KT, VT]):
    ...

reveal_type(MyFrozendict(), expected_text="MyFrozendict[Any, Any]")
reveal_type(MyFrozendict(baz=1), expected_text="MyFrozendict[str, int]")
reveal_type(MyFrozendict({"foo": "bar"}), expected_text="MyFrozendict[str, str]")
reveal_type(MyFrozendict(get_tuple_of_ints()), expected_text="MyFrozendict[int, int]")
