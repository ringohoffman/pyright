# https://github.com/python/typing/issues/548#issuecomment-970287830
from collections.abc import Callable, Mapping, MutableMapping
import collections

def valmap[K, V, MappedV, MapT[_K, _V]: MutableMapping[_K, _V]](
    func: Callable[[V], MappedV],
    d: Mapping[K, V],
    factory: type[MapT[K, MappedV]] = dict,
) -> MapT[K, MappedV]:
    rv = factory()
    rv.update(zip(d.keys(), map(func, d.values())))
    return rv

fib = {1: 2, 2: 3, 3: 5, 5: 8}

reveal_type(valmap(str, fib, collections.OrderedDict), expected_text="OrderedDict[int, str]")
