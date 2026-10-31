# This sample tests invalid constructor constraint shapes.

from __future__ import annotations


class Unary[T]:
    pass


class Binary[K, V]:
    pass


class Concrete:
    pass


# This should generate an error because the constraint alternatives have
# inconsistent arity (U is not used in Unary[T]).
def bad_arity[F[T, U]: (Unary[T], Binary[T, U])](value: F[int, str]) -> None:
    pass


# This should generate an error because a constructor family cannot mix
# generic and concrete constraints (T is not used in Concrete).
def bad_generic_mix[F[T]: (Unary[T], Concrete)](value: F[int]) -> None:
    pass


# This should generate an error in the initial HKT scope.
def rejects_type_var_tuple[*Ts](value: Ts[int]) -> None:
    pass


# This should generate an error in the initial HKT scope.
def rejects_param_spec[**P](value: P[int]) -> None:
    pass
