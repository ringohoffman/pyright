# in stub file

from __future__ import annotations

from typing import Any, Literal, overload, reveal_type


class Field[GT]:
    # on the line after the overload: error: Type variable "_T" used with arguments
    @overload
    def __new__[FieldT: Field[GT]](cls: type[FieldT[GT]], null: Literal[False] = False, *args: Any, **kwargs: Any) -> FieldT[GT]: ...
    @overload
    def __new__[FieldT: Field[GT]](cls: type[FieldT[GT]], null: Literal[True], *args: Any, **kwargs: Any) -> FieldT[GT | None]: ...
    def __new__(cls: Any, null: Any = False, *args: Any, **kwargs: Any) -> Any: ...
    def __get__(self, instance: Any, owner: Any) -> GT: ...

class CharField(Field[str]): ...
class IntegerField(Field[int]): ...
# etc...

# in code

class User:
  f1 = CharField(null=False)
  f2 = CharField(null=True)

reveal_type(User().f1, expected_text="str")
reveal_type(User().f2, expected_text="str | None")
