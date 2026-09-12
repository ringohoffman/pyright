# This sample specifies and tests Higher-Kinded Type (HKT) template currying
# and partial type constructor application in Pyright.

from typing import Any, reveal_type

# ==============================================================================
# Category A: Valid Template Currying (* -> * -> * curried to * -> *)
# ==============================================================================

class MyMap[K, V]:
    pass

class SubMap[K, V](MyMap[K, V]):
    pass

# Case A1: Fixing the first parameter (K=str), currying on the second (V)
def make_str_map[V, M: MyMap[str, V]](cls: type[M[V]], value: V) -> M[V]:
    raise NotImplementedError

m1 = make_str_map(MyMap, 42)
reveal_type(m1, expected_text="MyMap[str, int]")

m2 = make_str_map(SubMap, 42)
reveal_type(m2, expected_text="SubMap[str, int]")


# Case A2: Fixing the second parameter (V=int), currying on the first (K)
def make_int_val_map[K, M: MyMap[K, int]](cls: type[M[K]], key: K) -> M[K]:
    raise NotImplementedError

m3 = make_int_val_map(MyMap, "hello")
reveal_type(m3, expected_text="MyMap[str, int]")

m4 = make_int_val_map(SubMap, 3.14)
reveal_type(m4, expected_text="SubMap[float, int]")


# ==============================================================================
# Category B: Multi-step Currying (* -> * -> * -> * curried to * -> *)
# ==============================================================================

class Triad[A, B, C]:
    pass

class SubTriad[A, B, C](Triad[A, B, C]):
    pass

# Fixing A=int, B=str, leaving C free (arity 1)
def make_triad_c[C, T: Triad[int, str, C]](cls: type[T[C]], item: C) -> T[C]:
    raise NotImplementedError

t1 = make_triad_c(Triad, True)
reveal_type(t1, expected_text="Triad[int, str, bool]")

t2 = make_triad_c(SubTriad, 1.0)
reveal_type(t2, expected_text="SubTriad[int, str, float]")


# ==============================================================================
# Category C: Rejection of Uncurried Classes (No Template Provided)
# ==============================================================================

class UnaryBox[T]:
    pass

class BinaryBox[A, B]:
    pass

def expects_unary[T, F: UnaryBox[T]](val: F[int]) -> F[int]:
    raise NotImplementedError

# This should generate an error:
# BinaryBox has 2 type parameters, but type constructor F requires 1.
# Generic class "BinaryBox[int, int]" cannot be partially applied to satisfy type constructor "F".
b_two: BinaryBox[int, int] = BinaryBox()
expects_unary(b_two)


# ==============================================================================
# Category D: Arity Mismatch on Template-Curried Constructor
# ==============================================================================

# DictT: MyMap[str, V] has 1 free variable (V).
# Subscripting DictT with 2 arguments should generate an error:
# Too many type arguments provided for "DictT"; expected 1 but received 2
def invalid_curried_subscript[V, DictT: MyMap[str, V]](
    cls: type[DictT[int, str]]
) -> None:
    pass
