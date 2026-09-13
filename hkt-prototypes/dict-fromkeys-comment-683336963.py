# https://github.com/python/typing/issues/548#issuecomment-683336963
#
# Use case from Bas van Beek (@BvB93) / typeshed#3800:
# `dict.fromkeys(iterable, value)` creates a new mapping whose key type comes from
# `iterable`, value type from `value`, and container constructor from `cls`.
#
# Without HKT:
# `fromkeys` in typeshed had to hardcode `dict[T, S]`, forcing every dict subclass
# (OrderedDict, defaultdict, custom mappings) to manually duplicate `fromkeys` stubs.
#
# With HKT:
# Parameterizing the classmethod over `DictT: DictMapping[...]` preserves the derived
# class constructor (`DictMapping` vs `OrderedDictMapping`) with dynamically supplied key and value types.

from __future__ import annotations

import collections
from collections.abc import Iterable, Iterator, MutableMapping
from typing import Any, overload, reveal_type


class DictMapping[_KT, _VT](MutableMapping[_KT, _VT]):
    def __init__(self, mapping: dict[_KT, _VT] | None = None) -> None:
        self._data: dict[_KT, _VT] = dict(mapping) if mapping is not None else {}

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key: _KT) -> _VT:
        return self._data[key]

    def __setitem__(self, key: _KT, val: _VT) -> None:
        self._data[key] = val

    def __delitem__(self, key: _KT) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[_KT]:
        return iter(self._data)

    @classmethod
    @overload
    def fromkeys[_T, DictT: DictMapping[_T, Any | None]](
        cls: type[DictT[_T]], iterable: Iterable[_T], value: None = None, /
    ) -> DictT[_T]: ...

    @classmethod
    @overload
    def fromkeys[_T, _S, DictT: DictMapping[_T, _S]](
        cls: type[DictT[_T, _S]], iterable: Iterable[_T], value: _S, /
    ) -> DictT[_T, _S]: ...

    @classmethod
    def fromkeys(cls: Any, iterable: Iterable[Any], value: Any = None, /) -> Any:
        d = cls()
        for key in iterable:
            d[key] = value
        return d


class OrderedDictMapping[_KT, _VT](DictMapping[_KT, _VT]):
    pass


# 1. Base DictMapping preserves constructor with inferred key type and default None value
from_int_keys = DictMapping.fromkeys(list(range(10)))
reveal_type(from_int_keys, expected_text="DictMapping[int, Any | None]")

# 2. Base DictMapping preserves constructor with supplied value type
from_int_keys_with_value = DictMapping.fromkeys(list(range(10)), "food")
reveal_type(from_int_keys_with_value, expected_text="DictMapping[int, str]")

# 3. Subclass OrderedDictMapping automatically preserves its own constructor without overriding fromkeys
ordered_from_int_keys = OrderedDictMapping.fromkeys(list(range(10)))
reveal_type(ordered_from_int_keys, expected_text="OrderedDictMapping[int, Any | None]")

ordered_from_int_keys_with_value = OrderedDictMapping.fromkeys(list(range(10)), "food")
reveal_type(ordered_from_int_keys_with_value, expected_text="OrderedDictMapping[int, str]")

# 4. In-place functional check
assert isinstance(ordered_from_int_keys_with_value, OrderedDictMapping)
assert ordered_from_int_keys_with_value[0] == "food"


# 5. Higher-kinded container constraint in generic function
def f[DictT: dict[int, int]](int_to_int: DictT) -> DictT:
    return int_to_int


reveal_type(f({1: 1}), expected_text="dict[int, int]")
reveal_type(f(collections.OrderedDict({1: 1})), expected_text="OrderedDict[int, int]")
