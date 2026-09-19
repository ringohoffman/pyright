# https://github.com/python/typing/issues/548#issuecomment-4526032478
# Context: python/typeshed#15724 (Alex Waygood) & python/typing#548 (Joren Hammudoglu)
#
# Use case from typeshed: typing `builtins.frozendict.__new__` / `dict.__new__` constructors
# accurately across subclasses without erasing types or duplicating overloads.
#
# Without HKT:
# In standard Python, it is impossible to accurately type mapping constructors across subclasses:
# 1. `Self` cannot be used: `Self` is bound to the existing instance's type parameters and cannot
#    infer new key/value types from constructor arguments (e.g. `**kwargs: VT` or mapping arguments).
# 2. `SelfT: frozendict[KT, VT]` cannot be parameterized: In standard Python, `SelfT` is a concrete
#    TypeVar of kind `*`. Writing `SelfT[KT, VT]` is illegal ("Type variable used with arguments").
# 3. Typing `__new__` to return `frozendict[KT, VT]` erases subclass return types: calling
#    `MyFrozendict(baz=1)` produces base `frozendict[str, int]`, not `MyFrozendict[str, int]`.
# Stubs were forced to choose between type erasure on subclasses or demanding that every subclass
# redundantly copy-paste and maintain 5+ constructor overloads.
#
# With HKT:
# `SelfT` is captured as an unapplied/partially applied higher-kinded type constructor on `__new__`:
# - Full binary constructor: `cls: type[SelfT[KT, VT]] -> SelfT[KT, VT]`
# - Partially applied unary constructor: `cls: type[SelfT[VT]], **kwargs: VT -> SelfT[VT]` (with KT = str)
# Key/value types are inferred from constructor arguments while preserving the exact subclass type
# (`MyFrozendict[str, int]`), with zero subclass boilerplate.

from collections.abc import Iterable, Iterator, Mapping
from typing import Any, Protocol, overload, reveal_type

class SupportsKeysAndGetItem[_KT, _VT_co](Protocol):
    def keys(self) -> Iterable[_KT]: ...
    def __getitem__(self, key: _KT, /) -> _VT_co: ...


class frozendict[_KT, _VT](Mapping[_KT, _VT]):
    _data: dict[_KT, _VT]

    @overload
    def __new__[KT=Any, VT=Any, SelfT: frozendict[KT, VT] = frozendict[Any, Any]](
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
        instance = super().__new__(cls)
        data: dict[Any, Any] = {}
        if args:
            data.update(dict(args[0]))
        data.update(kwargs)
        instance._data = data
        return instance

    def copy(self) -> frozendict[_KT, _VT]:
        return type(self)(self)

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key: _KT, /) -> _VT:
        return self._data[key]

    def __reversed__(self) -> Iterator[_KT]:
        return reversed(self._data)

    def __iter__(self) -> Iterator[_KT]:
        return iter(self._data)

    def __hash__(self) -> int:
        return hash(frozenset(self._data.items()))


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

# Runtime functional validation
fd = frozendict(baz=1)
assert isinstance(fd, frozendict)
assert fd["baz"] == 1
assert len(fd) == 1

mfd = MyFrozendict({"foo": "bar"})
assert isinstance(mfd, MyFrozendict)
assert mfd["foo"] == "bar"
assert len(mfd) == 1
