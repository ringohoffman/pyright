# This sample tests PEP 695 constraints over generic constructor origins.

from __future__ import annotations

from typing import reveal_type


class Container[T]:
    pass


class SpecialContainer[T](Container[T]):
    pass


class Other[T]:
    pass


def transform[A, B, ContainerT: Container[A]](value: ContainerT[A], new_value_type: type[B]) -> ContainerT[B]:
    raise NotImplementedError


special_container = transform(SpecialContainer[int](), str)
reveal_type(special_container, expected_text="SpecialContainer[str]")

# This should generate an error because Other does not derive from Container.
transform(Other[int](), str)

