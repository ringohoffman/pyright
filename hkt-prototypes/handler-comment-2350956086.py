# https://github.com/python/typing/issues/548#issuecomment-2350956086
#
# Use case from nerodono:
# Generic wrapper class `Ext[Inner]` providing a `modify` method that transforms
# the wrapped inner type (`Inner` -> `O`) while preserving the exact subclass
# (`MyExt[O]` or `PredicateExt[O]`) rather than erasing to base `Ext[O]`.
#
# Without HKT:
# In standard Python (PEP 484 / PEP 695):
# - `Self` represents the current instance type but cannot be re-parameterized with
#   a new inner type argument (e.g. `Self[O]` is illegal).
# - Standard TypeVars are concrete types (kind *), so `E[O]` cannot take arguments.
# As a result, `Ext.modify` must return `Ext[O]`. Any subclass (like `MyExt` or
# `PredicateExt`) has its concrete type erased, losing all subclass methods and
# specialized protocol capabilities unless every subclass redundantly re-implements
# `modify`.
#
# With HKT:
# `Ext.modify` captures the subclass as a type constructor `E[T]: Ext[Any]` on `self`:
#
#     def modify[O, E[T]: Ext[Any]](self: E[Inner], f: Callable[[Inner], O]) -> E[O]:
#         ...
#
# Subclasses inherit `modify` once, automatically preserving their specialized class
# identity while updating the wrapped inner type.

from collections.abc import Callable
from typing import Any, Protocol, Self, reveal_type


# 1. Modify Protocol and Ext Wrapper Preserving Subclasses
class Modify(Protocol):
    def modify[O](self, f: Callable[[Self], O], /) -> O: ...


class Ext[Inner]:
    inner: Inner

    def __init__(self, inner: Inner) -> None:
        self.inner = inner

    def modify[O, E[T]: Ext[Any]](self: E[Inner], f: Callable[[Inner], O]) -> E[O]:
        cls = type(self)
        return cls(f(self.inner))  # type: ignore


class MyExt[Inner](Ext[Inner]):
    def another_method(self) -> str:
        return "another method preserved!"


# Calling .modify on MyExt preserves MyExt (does NOT erase to Ext[O])
me = MyExt(123)
me_modified = me.modify(str)
reveal_type(me_modified, expected_text="MyExt[str]")
assert me_modified.another_method() == "another method preserved!"
assert me_modified.inner == "123"
assert isinstance(me_modified, MyExt)


# 2. Handler & Predicate Specialization with PredicateExt
class Handler[I, O](Protocol):
    def __call__(self, input: I, /) -> O: ...


class Predicate[I](Handler[I, bool], Protocol):
    pass


class And[I]:
    def __init__(self, lhs: Predicate[I], rhs: Predicate[I]) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, input: I, /) -> bool:
        return self.lhs(input) and self.rhs(input)


class PredicateExt[P](Ext[P]):
    def and_[I](self: PredicateExt[Predicate[I]], rhs: Predicate[I]) -> PredicateExt[Predicate[I]]:
        return self.modify(lambda lhs: And(lhs, rhs))


class IsPositive:
    def __call__(self, input: int, /) -> bool:
        return input > 0


class IsEven:
    def __call__(self, input: int, /) -> bool:
        return input % 2 == 0


# Calling .and_() on PredicateExt preserves PredicateExt and composition
p1: PredicateExt[Predicate[int]] = PredicateExt(IsPositive())
p2: Predicate[int] = IsEven()
p_and = p1.and_(p2)
reveal_type(p_and, expected_text="PredicateExt[Predicate[int]]")

# Runtime execution validation
assert isinstance(p_and, PredicateExt)
assert p_and.inner(4) is True
assert p_and.inner(3) is False
assert p_and.inner(-2) is False
