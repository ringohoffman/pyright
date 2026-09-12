# This sample tests mismatched type parameter counts in Higher-Kinded Type (HKT)
# constructor applications, both with and without overloads.

from typing import Any, Protocol, overload, reveal_type

class Box[T]:
    pass

class OtherBox[T]:
    pass

class TupleBox[A, B](Box[A]):
    pass

# -------------------------------------------------------------
# 1. Non-overloaded HKT constructor parameter
# -------------------------------------------------------------
def accepts_unary_hkt[T, Constructor: (Box[T], OtherBox[T])](value: Constructor[int]) -> Constructor[int]:
    raise NotImplementedError

tb_two: TupleBox[int, int] = TupleBox()

# Passing TupleBox (2 type parameters) to unary constructor Constructor (1 type parameter)
# triggers reportArgumentType with the type parameter count mismatch addendum:
#   "TupleBox[int, int]" has 2 type parameters, but type constructor "Constructor@accepts_unary_hkt" expects 1
accepts_unary_hkt(tb_two)

# -------------------------------------------------------------
# 2. Overloaded HKT constructor function
# -------------------------------------------------------------
@overload
def overloaded_unary_hkt[T, Constructor: (Box[T], OtherBox[T])](value: Constructor[int]) -> Constructor[int]: ...
@overload
def overloaded_unary_hkt(value: str) -> str: ...
def overloaded_unary_hkt(value: Any) -> Any:
    return value

# Overload evaluation attempts closest match and provides reportCallIssue + reportArgumentType
overloaded_unary_hkt(tb_two)

# -------------------------------------------------------------
# 3. Class overloaded constructor (__new__) with HKT TypeVar
# -------------------------------------------------------------
class mock_frozendict[KT, VT]:
    # Overload 1: SelfT expects 1 type parameter because key is fixed to str
    @overload
    def __new__[V, SelfT: mock_frozendict[str, V]](
        cls: type[SelfT[V]],
        /,
        **kwargs: V,
    ) -> SelfT[V]: ...

    # Overload 2: SelfT expects 2 type parameters
    @overload
    def __new__[K, V, SelfT: mock_frozendict[K, V]](
        cls: type[SelfT[K, V]],
        iterable: list[tuple[K, V]],
        /,
    ) -> SelfT[K, V]: ...

    def __new__(cls, *args, **kwargs) -> Any:
        pass

class MySubFrozendict[KT, VT](mock_frozendict[KT, VT]):
    pass

# Calling MySubFrozendict(baz=1) specializes SelfT to MySubFrozendict:
# MySubFrozendict inherits from mock_frozendict[KT, VT], and the bound mock_frozendict[str, V]
# specializes KT -> str, V -> int, yielding MySubFrozendict[str, int].
reveal_type(MySubFrozendict(baz=1), expected_text="MySubFrozendict[str, int]")

# Calling with arguments matching Overload 2 succeeds:
items: list[tuple[str, str]] = [("foo", "bar")]
reveal_type(MySubFrozendict(items), expected_text="MySubFrozendict[str, str]")


