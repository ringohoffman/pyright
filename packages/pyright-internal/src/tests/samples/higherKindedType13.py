# This sample tests invalid constructor constraint shapes.

from __future__ import annotations

from typing import Generic, ParamSpec, TypeVar, TypeVarTuple

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class Unary(Generic[T]):
    pass


class Binary(Generic[K, V]):
    pass


class Concrete:
    pass


MixedArity = TypeVar("MixedArity", Unary[T], Binary[K, V])
MixedGeneric = TypeVar("MixedGeneric", Unary[T], Concrete)


# This should generate an error because constructor constraints have inconsistent arity.
def bad_arity(value: MixedArity[int]) -> None:
    pass


# This should generate an error because a constructor family cannot mix generic and concrete constraints.
def bad_generic_mix(value: MixedGeneric[int]) -> None:
    pass


Ts = TypeVarTuple("Ts")
P = ParamSpec("P")


# This should generate an error in the initial HKT scope.
def rejects_type_var_tuple(value: Ts[int]) -> None:
    pass


# This should generate an error in the initial HKT scope.
def rejects_param_spec(value: P[int]) -> None:
    pass


# PEP 695 equivalents.
# This should generate an error because constructor constraints have inconsistent arity.
def bad_arity_pep695[T, K, V, F: (Unary[T], Binary[K, V])](value: F[int]) -> None:
    pass


# This should generate an error because a constructor family cannot mix generic and concrete constraints.
def bad_generic_mix_pep695[T, F: (Unary[T], Concrete)](value: F[int]) -> None:
    pass


# This should generate an error in the initial HKT scope.
def rejects_type_var_tuple_pep695[*Ts](value: Ts[int]) -> None:
    pass


# This should generate an error in the initial HKT scope.
def rejects_param_spec_pep695[**P](value: P[int]) -> None:
    pass