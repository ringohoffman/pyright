# Context: typeshed stubs gevent/pool.pyi (lines 166-199)
# Reference: https://github.com/jorenham/hkt-survey/blob/main/gevent_group_greenlet.md
#
# Use case from gevent:
# `gevent.pool.Group` manages a group of greenlets. The group itself is generic in the
# greenlet constructor `G` (defaulting to `Greenlet`), allowing methods like `spawn`
# to return the specific greenlet type (e.g. `MyGreenlet[int]`) while methods like `add`
# enforce that all greenlets added to the group match constructor `G`.
#
# Without HKT:
# In standard Python (typeshed stubs for gevent):
# The stub contains this comment:
#   "We would need higher-kinded TypeVars if we wanted to give up neither -- i.e. be
#    generic in Greenlet and keep spawn/apply return types specific, while still mixing
#    greenlets of different result types in one group."
# 1. Parameterizing Group by a concrete Greenlet type `Group[Greenlet[R]]` pins every greenlet
#    in the group to the same result type `R`, making it impossible to mix `Greenlet[int]`
#    and `Greenlet[str]` in the same group.
# 2. Parameterizing Group as `Group[Greenlet[Any]]` allows heterogeneous greenlets, but completely
#    erases the return type of `spawn(make_int)` down to `Greenlet[Any]`, losing subclass methods
#    like `MyGreenlet.link()`.
#
# With HKT:
# The class itself is generic in the type constructor `G[T]: Greenlet[T]`:
#     class Group[G[T]: Greenlet[T] = Greenlet[T]]:
#         def spawn[R](self, func: Callable[[], R]) -> G[R]: ...
#         def add(self, greenlet: G[Any]) -> None: ...
#
# Note on constructor defaults:
# Both forms of constructor defaults are supported via eta-reduction:
#   - Applied template default: `G[T]: Greenlet[T] = Greenlet[T]`
#   - Bare constructor default:  `G[T]: Greenlet[T] = Greenlet`
# Both forms eta-reduce to the unapplied constructor `Greenlet` of kind * -> *.
# - `Group` can hold greenlets with different result types `R` (via `G[Any]`).
# - `g.spawn(make_int)` returns the exact specialized greenlet `MyGreenlet[int]`.
# - Passing a mismatched greenlet constructor to `add()` is rejected at type-check time.

from collections.abc import Callable
from typing import Any, reveal_type


class Greenlet[R]:
    def __init__(self, result: R) -> None:
        self.result = result


# Form 1: Applied template default `G[T]: Greenlet[T] = Greenlet[T]`
class Group[G[T]: Greenlet[T] = Greenlet[T]]:
    def __init__(self, ctor: type[G] = Greenlet) -> None:
        self.ctor = ctor
        self.greenlets: list[Greenlet[Any]] = []

    def add(self, greenlet: G[Any]) -> None:
        self.greenlets.append(greenlet)

    def spawn[R](self, func: Callable[[], R]) -> G[R]:
        return self.ctor(func())  # type: ignore

    def apply[R](self, func: Callable[[], R]) -> R:
        return func()


# Form 2: Bare constructor default `G[T]: Greenlet[T] = Greenlet`
class BareGroup[G[T]: Greenlet[T] = Greenlet]:
    def __init__(self, ctor: type[G] = Greenlet) -> None:
        self.ctor = ctor

    def spawn[R](self, func: Callable[[], R]) -> G[R]:
        return self.ctor(func())  # type: ignore


class MyGreenlet[R](Greenlet[R]):
    def link(self) -> str:
        return f"linked: {self.result}"


# 1. Instantiate Group by passing unapplied subclass constructor MyGreenlet directly:
# Pyright infers G = MyGreenlet without Unknown leakage or manual type arguments
g = Group(MyGreenlet)
reveal_type(g, expected_text="Group[MyGreenlet[R@MyGreenlet]]")

# 2. spawn infers R = int and returns specialized MyGreenlet[int]
def make_int() -> int:
    return 42

spawned = g.spawn(make_int)
reveal_type(spawned, expected_text="MyGreenlet[int]")

# 3. Specialized subclass method .link() is preserved (today: Greenlet has no attribute "link")
assert spawned.link() == "linked: 42"

# 4. apply runs the callable directly and returns the unwrapped result R
app = g.apply(lambda: "hello")
reveal_type(app, expected_text="str")
assert app == "hello"

# 5. Default Group call Group() defaults constructor to base Greenlet via applied default `Greenlet[T]`
g_default = Group()
reveal_type(g_default, expected_text="Group[Greenlet[R@Greenlet]]")

spawned_default = g_default.spawn(lambda: [1, 2, 3])
reveal_type(spawned_default, expected_text="Greenlet[list[int]]")

# 6. BareGroup call BareGroup() defaults constructor to base Greenlet via bare default `Greenlet`
bg_default = BareGroup()
reveal_type(bg_default, expected_text="BareGroup[Greenlet[R@Greenlet]]")

bg_spawned = bg_default.spawn(lambda: "bare")
reveal_type(bg_spawned, expected_text="Greenlet[str]")
