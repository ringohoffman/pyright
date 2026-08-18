# https://github.com/python/typing/issues/548#issuecomment-621790339
from collections.abc import Coroutine
from typing import Any, TypeVar, reveal_type

T = TypeVar('T', bool, bytes, str, int, float, None)
type Result[T] = Coroutine[Any, Any, T]

class MethodFacade[BoolT, BytesT, StrT, IntT, FloatT, NoneT]:
    def method_1(self, *args: Any) -> StrT:
        ...

    def method_2(self, *args: Any) -> NoneT:
        ...

    def method_3(self, *args: Any) -> BoolT:
        ...

    def method_200(self, *args: Any) -> IntT:
        ...


# no HKT

class CoroutineGenerator(MethodFacade[Result[bool], Result[bytes], Result[str], Result[int], Result[float], Result[None]]):
    ...

class NoneGenerator(MethodFacade[None, None, None, None, None, None]):
    ...


coroutine_generator = CoroutineGenerator()
reveal_type(coroutine_generator.method_1(), expected_str="Coroutine[Any, Any, str]")

none_generator = NoneGenerator()
reveal_type(none_generator.method_1(), expected_str="None")

# HKT
# Goal: Pass a single type constructor (e.g., Result or ConstNone) to parameterize all method return types.

from typing import Protocol


# 1. Define a template / protocol to declare that `WrapperT` is a generic type constructor (kind * -> *)
class WrapperTemplate[T](Protocol):
    ...


# 2. Declare `WrapperT` with a constructor template constraint `WrapperT: WrapperTemplate[X]`
# (or union of origins: `WrapperT: (Result[X], ConstNone[X])`)
class GenericFacade[X: (bool, bytes, str, int, float, None), WrapperT: WrapperTemplate[X]]:
    def method_1(self, *args: Any) -> WrapperT[str]:
        ...

    def method_2(self, *args: Any) -> WrapperT[None]:
        ...

    def method_3(self, *args: Any) -> WrapperT[bool]:
        ...

    def method_200(self, *args: Any) -> WrapperT[int]:
        ...


class CoroutineFacade[X: (bool, bytes, str, int, float, None)](GenericFacade[X, Coroutine[Any, Any, X]]):
    ...


type ConstNone[T] = None


class NoneFacade[X: (bool, bytes, str, int, float, None)](GenericFacade[X, ConstNone[X]]):
    ...


coroutine_facade = CoroutineFacade()
reveal_type(coroutine_facade.method_1(), expected_str="Coroutine[Any, Any, str]")

none_facade = NoneFacade()
reveal_type(none_facade.method_1(), expected_str="None")
