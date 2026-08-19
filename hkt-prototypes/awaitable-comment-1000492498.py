# https://github.com/python/typing/issues/548#issuecomment-1000492498
from collections.abc import Awaitable

type Identity[T] = T


class A[WrapperT[T] = Identity[T]]:
   def foo(self)-> WrapperT[int]: ...
   def bar(self)-> WrapperT[bool]: ...


class AsyncA(A[Awaitable]):
   ...


reveal_type(A().foo(), expected_text="int")
reveal_type(AsyncA().foo(), expected_text="Awaitable[int]")
