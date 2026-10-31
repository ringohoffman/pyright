# This sample tests that a type constructor parameter solved from a
# subclass preserves the most-derived generic constructor through
# multi-level inheritance, and that a concrete (non-generic) subclass
# resolves to its nearest generic base.


class Container[T]:
    def __init__(self, value: T) -> None:
        self.value = value


class MidContainer[T](Container[T]):
    pass


class LeafContainer[T](MidContainer[T]):
    pass


# Concrete subclass: no type parameters of its own.
class IntContainer(MidContainer[int]):
    pass


def transform[T, U, F[X]: Container[X]](value: F[T], new_type: type[U]) -> F[U]:
    raise NotImplementedError


reveal_type(transform(Container(1), str), expected_text="Container[str]")
reveal_type(transform(MidContainer(1), str), expected_text="MidContainer[str]")
reveal_type(transform(LeafContainer(1), str), expected_text="LeafContainer[str]")

# IntContainer has arity 0, so the solver falls back to its nearest generic
# base in the MRO, MidContainer.
reveal_type(transform(IntContainer(1), str), expected_text="MidContainer[str]")


def rewrap[F[X]: Container[X]](value: F[int]) -> F[int]:
    return value


reveal_type(rewrap(LeafContainer(1)), expected_text="LeafContainer[int]")


class Unrelated[T]:
    pass


# This should generate an error because Unrelated does not derive from Container.
transform(Unrelated[int](), str)
