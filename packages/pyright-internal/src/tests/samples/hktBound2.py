# This sample tests that type constructor parameters require all inner type parameters
# to be referenced in their upper bound or constraint alternatives.

from typing import Any
from collections.abc import Callable, Iterable

class Functor[A]:
    pass

# This should generate an error because T is not used in the bound Functor[Any].
def bad_unused_inner_bound[A, B, F[T]: Functor[Any]](xs: F[A], f: Callable[[A], B]) -> F[B]:
    ...

# This should generate an error because T is not used in the bound Functor[int].
def bad_concrete_inner_bound[A, B, F[T]: Functor[int]](xs: F[A], f: Callable[[A], B]) -> F[B]:
    ...

# This should generate an error because K is not used in the bound dict[str, V].
def bad_partial_unused_inner[A, B, F[K, V]: dict[str, V]](xs: F[A, B]) -> None:
    ...

# This should generate an error because T is not used in the second constraint (set[Any]).
def bad_unused_in_constraint_alt[A, F[T]: (list[T], set[Any])](xs: F[A]) -> None:
    ...

# Valid: T is used in bound Functor[T].
def good_bound[A, B, F[T]: Functor[T]](xs: F[A], f: Callable[[A], B]) -> F[B]:
    ...

# Valid: union bound where T is used in at least one part of the union.
def good_union_bound[A, F[T]: (Iterable[T] | None)](xs: F[A]) -> None:
    ...

# Valid: both K and V used in constraint alternatives.
def good_constraints[A, B, F[K, V]: (dict[K, V], dict[V, K])](xs: F[A, B]) -> None:
    ...
