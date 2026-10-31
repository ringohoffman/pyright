# This sample tests higher-kinded coroutine wrapper parameterization on a facade class (Samuel Colvin async redis pattern).

from __future__ import annotations

from collections.abc import Coroutine
from typing import Any, Protocol, reveal_type

type Result[T] = Coroutine[Any, Any, T]
type ConstNone[T] = None


class WrapperTemplate[T](Protocol):
    pass


class GenericFacade[WrapperT[X: (bool, bytes, str, int, float, None)]: WrapperTemplate[X]]:
    def method_1(self, *args: Any) -> WrapperT[str]:
        raise NotImplementedError

    def method_2(self, *args: Any) -> WrapperT[None]:
        raise NotImplementedError

    def method_3(self, *args: Any) -> WrapperT[bool]:
        raise NotImplementedError

    def method_200(self, *args: Any) -> WrapperT[int]:
        raise NotImplementedError


class CoroutineFacade(GenericFacade[Result]):
    pass


class NoneFacade(GenericFacade[ConstNone]):
    pass


coroutine_facade = CoroutineFacade()
reveal_type(coroutine_facade.method_1(), expected_text="Coroutine[Any, Any, str]")
reveal_type(coroutine_facade.method_2(), expected_text="Coroutine[Any, Any, None]")
reveal_type(coroutine_facade.method_3(), expected_text="Coroutine[Any, Any, bool]")
reveal_type(coroutine_facade.method_200(), expected_text="Coroutine[Any, Any, int]")

none_facade = NoneFacade()
reveal_type(none_facade.method_1(), expected_text="None")
reveal_type(none_facade.method_2(), expected_text="None")
reveal_type(none_facade.method_3(), expected_text="None")
reveal_type(none_facade.method_200(), expected_text="None")
