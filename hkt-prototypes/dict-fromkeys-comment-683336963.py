from __future__ import annotations

from collections.abc import Iterable, MutableMapping
from typing import Any, overload, reveal_type


class _dict2[_KT, _VT](MutableMapping[_KT, _VT]):
    @classmethod
    @overload
    def fromkeys[_T, DictT: _dict2[_T, Any | None]](cls: type[DictT[_T]], iterable: Iterable[_T], value: None = None, /) -> DictT[_T]: ...
    @classmethod
    @overload
    def fromkeys[_T, _S, DictT: _dict2[_T, _S]](cls: type[DictT[_T, _S]], iterable: Iterable[_T], value: _S, /) -> DictT[_T, _S]: ...
    @classmethod
    def fromkeys(cls, iterable: Any, value: Any = None, /) -> Any: ...


class _OrderedDict2[_KT, _VT](_dict2[_KT, _VT]):
    ...


from_int_keys2 = _dict2.fromkeys(list(range(10)))
reveal_type(from_int_keys2, expected_str="_dict2[int, Any | None]")
from_int_keys_with_value2 = _dict2.fromkeys(list(range(10)), "food")
reveal_type(from_int_keys_with_value2, expected_str="_dict2[int, str]")

ordered_from_int_keys2 = _OrderedDict2.fromkeys(list(range(10)))
reveal_type(ordered_from_int_keys2, expected_str="_OrderedDict2[int, Any | None]")
ordered_from_int_keys_with_value2 = _OrderedDict2.fromkeys(list(range(10)), "food")
reveal_type(ordered_from_int_keys_with_value2, expected_str="_OrderedDict2[int, str]")

type DictToInt[T] = dict[T, int]


def f[DictT: dict[int, int]](int_to_int: DictT) -> DictT:
    return int_to_int

reveal_type(f({1: 1}), expected_str="dict[int, int]")

import collections

reveal_type(f(collections.OrderedDict({1: 1})), expected_str="OrderedDict[int, int]")
