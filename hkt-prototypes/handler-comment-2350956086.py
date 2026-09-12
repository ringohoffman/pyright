# https://github.com/python/typing/issues/548#issuecomment-2350956086
#
# Use case: A generic wrapper class `Ext[Inner]` that provides a method `modify`
# which transforms the inner type from `Inner` to `O`, while preserving the exact
# subclass of `Ext` (e.g. `MyExt[O]` or `PredicateExt[O]`), rather than erasing
# back to `Ext[O]`.
#
# In Python, `Self` cannot be parameterized as `Self[O]`. With Higher-Kinded Types (HKT),
# this is expressed cleanly using a type constructor parameter `E[T]: Ext[Any]` on `self`:
#
#     def modify[O, E[T]: Ext[Any]](self: E[Inner], f: Callable[[Inner], O]) -> E[O]:
#         ...

from collections.abc import Callable
from typing import Any, Protocol, Self, reveal_type

# ==============================================================================
# Part 1: Modify Protocol and Ext Wrapper Preserving Subclasses
# ==============================================================================

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

# 1. Calling .modify on MyExt preserves MyExt (does NOT erase to Ext[O])
me = MyExt(123)
me_modified = me.modify(str)
reveal_type(me_modified, expected_text="MyExt[str]")
assert me_modified.another_method() == "another method preserved!"

# ==============================================================================
# Part 2: Handler & Predicate Specialization with PredicateExt
# ==============================================================================

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

# 2. When calling .and_() on PredicateExt, the returned type remains PredicateExt
p1: PredicateExt[Predicate[int]] = PredicateExt(IsPositive())
p2: Predicate[int] = IsEven()
p_and = p1.and_(p2)
reveal_type(p_and, expected_text="PredicateExt[Predicate[int]]")
