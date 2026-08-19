# https://github.com/python/typing/issues/548#issuecomment-919555518

from collections.abc import Collection
from typing import Any, TypeGuard, reveal_type

def all_elements_type[V, CollectionT: Collection[V]](
    collection: CollectionT[object],
    element_type: type[V],
) -> TypeGuard[CollectionT[V]]:
    return all(isinstance(t, element_type) for t in collection)

my_list: list[Any] = []
if all_elements_type(my_list, int):
    reveal_type(my_list, expected_text="list[int]")
    my_sum = sum(my_list)
