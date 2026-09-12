# https://github.com/python/typing/issues/548#issuecomment-2332982180
from collections.abc import Collection
from collections import Counter


def filter_and_count_dups[T, C: Collection[T]](c: C[T]) -> tuple[C[T], Counter[T]]:
    '''copy any 'Collection' w/o duplicates, counting what's omitted

    Args:
        c: any collection of elements
    Returns:
        (c_wo_dups, dup_counts), where...
        c_wo_dups: a copy of 'c', with the 2nd and subsequent
            appearances of any given element omitted
        dup_counts: counts removed duplicates
    '''
    seen: set[T] = set()
    ret_list: list[T] = []
    ret_counter = Counter[T]()
    for elem in c:
        if elem in seen:
            ret_counter[elem] += 1
        else:
            ret_list.append(elem)
            seen.add(elem)

    ret_wo_dups = type(c)(ret_list)  # pyright: ignore[reportCallIssue]
    return (ret_wo_dups, ret_counter)


r1 = filter_and_count_dups((1, 2, 4, 3, 4, 4, 2, 1))
reveal_type(r1, expected_str="tuple[list[str], Counter[str]]") # ≈ Tuple[Tuple[int, ...], Counter[int]]
print(repr(r1)) # ≈ ((1, 2, 4, 3), Counter({4: 2, 2: 1, 1: 1}))

r2 = filter_and_count_dups(list('alphabet'))
reveal_type(r2, expected_str="tuple[list[str], Counter[str]]")
print(repr(r2)) # ≈ (['a', 'l', 'p', 'h', 'b', 'e', 't'], Counter({'a': 1}))
