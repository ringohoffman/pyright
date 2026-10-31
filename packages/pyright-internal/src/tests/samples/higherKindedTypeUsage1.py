# This sample tests the checker rules for how a type constructor parameter
# may be used within a function signature.

from typing import Iterable


# A constructor used in a single parameter is solvable, so the usual
# "appears only once" warning does not apply.
def accepts_any_container[F[T]](x: F[int]) -> None: ...


# A constructor that appears in a parameter and the return type is the
# common case.
def swap[F[T]](x: F[int]) -> F[str]: ...


# This should generate an error because F appears only in the return type
# and can never be solved from the arguments.
def make_container[F[T]](n: int) -> F[int]: ...


# This should generate an error because D appears only in the return type.
def make_mapping[K, V, D: dict[K, V]](k: K, v: V) -> D[K, V]: ...


# A constructor that appears only in a parameter with a default is still
# solvable from an explicit argument, so no error here.
def with_default[F[T]: Iterable[T]](x: F[int] | None = None) -> F[int]: ...
