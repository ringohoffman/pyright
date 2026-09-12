# This sample tests higher-kinded type constructor application in function body
# where an applied TypeVar parameter is iterated and checked against local collections.

from collections.abc import Collection
from collections import Counter

def filter_and_count_dups[T, C: Collection[T]](c: C[T]) -> tuple[C[T], Counter[T]]:
    seen: set[T] = set()
    ret_list: list[T] = []
    ret_counter = Counter[T]()
    for elem in c:
        if elem in seen:
            ret_counter[elem] += 1
        else:
            ret_list.append(elem)
            seen.add(elem)

    # Note: Collection is an ABC so type(c)(...) cannot be called without constructor protocol
    ret_wo_dups = c
    return (ret_wo_dups, ret_counter)

r1 = filter_and_count_dups((1, 2, 4, 3, 4, 4, 2, 1))
reveal_type(r1, expected_text="tuple[tuple[Literal[1, 2, 4, 3]], Counter[Literal[1, 2, 4, 3]]]")

r2 = filter_and_count_dups(list('alphabet'))
reveal_type(r2, expected_text="tuple[list[str], Counter[str]]")
