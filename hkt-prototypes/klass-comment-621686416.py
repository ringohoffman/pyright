# https://github.com/python/typing/issues/548#issuecomment-621686416

from typing import Any, Protocol, reveal_type


class SinglePositionalConstructible[T](Protocol):
    def __init__(self, value: T, /, *args: Any, **kwargs: Any) -> None:
        ...

class Box[T]:
     def __init__(self, my_value: T, some_kwarg: int | None = None) -> None:
          ...

def create[K, T: SinglePositionalConstructible[K]](klass: type[T[Any]], value: K) -> T[K]:
     return klass(value)


reveal_type(create(Box, "a"), expected_text="Box[str]")


def unbox(x: SinglePositionalConstructible[int]) -> int:
     return 1

unbox(Box(1))
