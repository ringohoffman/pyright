# This sample tests a type constructor parameter used in a TypeIs return
# type to narrow a container's element type while preserving the container.

from typing import Collection, TypeIs


def all_of_type[T, C[X]: Collection[X]](values: C[object], element_type: type[T]) -> TypeIs[C[T]]:
    return all(isinstance(v, element_type) for v in values)


def func1(items: list[object], pairs: set[object]):
    if all_of_type(items, int):
        reveal_type(items, expected_text="list[int]")
    else:
        reveal_type(items, expected_text="list[object]")

    if all_of_type(pairs, str):
        reveal_type(pairs, expected_text="set[str]")
