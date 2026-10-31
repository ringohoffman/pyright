/// <reference path="typings/fourslash.d.ts" />

// @filename: pyrightconfig.json
//// {
////   "pythonVersion": "3.16"
//// }

// @filename: test.py
//// from collections import OrderedDict
////
//// def swap[[|/*decl*/F|][T]](x: F[int]) -> [|/*applied*/F|][str]: ...
////
//// [|/*callList*/result1|] = swap([1, 2])
//// [|/*callSet*/result2|] = swap({1, 2})
////
//// class Mapping[KT, VT]:
////     @classmethod
////     def fromkeys[T, S, D[K, V]: Mapping[K, V]](cls: type[D[T, S]], keys: list[T], value: S) -> D[T, S]: ...
////
//// class Ordered[KT, VT](Mapping[KT, VT]): ...
////
//// [|/*fromkeys*/result3|] = Ordered.fromkeys(["a"], 1)

helper.verifyHover('markdown', {
    decl: '```python\n(type parameter) F[T]: TypeVar\n```',
    applied: '```python\n(type parameter) F[T]: type[F@swap]\n```',
    callList: '```python\n(variable) result1: list[str]\n```',
    callSet: '```python\n(variable) result2: set[str]\n```',
    fromkeys: '```python\n(variable) result3: Ordered[str, int]\n```',
});
