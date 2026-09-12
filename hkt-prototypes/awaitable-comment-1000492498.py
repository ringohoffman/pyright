# https://github.com/python/typing/issues/548#issuecomment-1000492498
from collections.abc import Awaitable

type Identity[T] = T


class A[WrapperT[T] = Identity[T]]:
   def foo(self)-> WrapperT[int]: ...
   def bar(self)-> WrapperT[bool]: ...



# should this be defined as AsyncA(A[Awaitable[T]]) ? it seems strange that we don't declare the argument as a type constructor / generic type constructor ... what if we wanted to define it as a partially generic type constructor?
# and what would the real implementation look like? how do we actually turn supplying A[Awaitable] into a switch to actually return Awaitable?
class AsyncA(A[Awaitable]):
   ...


reveal_type(A().foo(), expected_text="int")
reveal_type(AsyncA().foo(), expected_text="Awaitable[int]")
