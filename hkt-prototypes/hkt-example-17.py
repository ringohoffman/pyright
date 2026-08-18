# This sample tests higher-kinded constructor variables with concrete vs generic subclasses.

from __future__ import annotations

from typing import Any, Literal, overload, reveal_type


class Field[GT]:
    def __get__(self, instance: Any, owner: Any) -> GT: ...


# Case 1: Fixed-dtype subclasses match through generic base constructor Field.
def make_field[GT, FieldT: Field[GT]](
    cls: type[FieldT[GT]], null: Literal[False] = False
) -> FieldT[GT]:
    raise NotImplementedError


def make_field_nullable[GT, FieldT: Field[GT]](
    cls: type[FieldT[GT]], null: Literal[True]
) -> FieldT[GT | None]:
    raise NotImplementedError


class CharField(Field[str]):
    pass


class User1:
    f1 = make_field(CharField, null=False)
    f2 = make_field_nullable(CharField, null=True)


reveal_type(User1().f1, expected_text="str")
reveal_type(User1().f2, expected_text="str | None")


# Case 2: Generic subclasses preserve constructor arity (arity 1) and CAN match FieldT[GT].
class GenericCharField[T: str | None = str](Field[T]):
    pass


class User2:
    f1 = make_field(GenericCharField[str], null=False)
    f2 = make_field_nullable(GenericCharField[str], null=True)


reveal_type(User2().f1, expected_text="str")
reveal_type(User2().f2, expected_text="str | None")


# Case 3: Returning a base specialization without higher-kinded re-parameterization.
class BaseField[GT]:
    @overload
    def __new__[F: BaseField[Any]](
        cls: type[F], null: Literal[False] = False, *args: Any, **kwargs: Any
    ) -> F: ...
    @overload
    def __new__(
        cls: Any, null: Literal[True], *args: Any, **kwargs: Any
    ) -> BaseField[GT | None]: ...
    def __new__(cls: Any, null: Any = False, *args: Any, **kwargs: Any) -> Any: ...
    def __get__(self, instance: Any, owner: Any) -> GT: ...


class ConcreteCharField(BaseField[str]):
    pass


class User3:
    f1 = ConcreteCharField(null=False)
    f2 = ConcreteCharField(null=True)


reveal_type(User3().f1, expected_text="str")
reveal_type(User3().f2, expected_text="str | None")

# Case 4: Re-parameterized method signature on generic base class.
class BaseField2[GT]:
    @overload
    def __new__[F: BaseField2[GT]](
        cls: type[F[GT]], null: Literal[False] = False, *args: Any, **kwargs: Any
    ) -> F[GT]: ...
    @overload
    def __new__[F: BaseField2[GT]](
        cls: type[F[GT]], null: Literal[True], *args: Any, **kwargs: Any
    ) -> F[GT | None]: ...
    def __new__(cls: Any, null: Any = False, *args: Any, **kwargs: Any) -> Any: ...
    def __get__(self, instance: Any, owner: Any) -> GT: ...


class SpecialField2[GT](BaseField2[GT]):
    ...

class ConcreteCharField2(SpecialField2[str]):
    pass


reveal_type(ConcreteCharField2(null=False), expected_text="SpecialField2[str]")
reveal_type(ConcreteCharField2(null=True), expected_text="SpecialField2[str | None]")

class User4:
    f1 = ConcreteCharField2(null=False)
    f2 = ConcreteCharField2(null=True)


reveal_type(User4().f1, expected_text="str")
reveal_type(User4().f2, expected_text="str | None")

# Case 5: Explicit base class overload signatures without type constructor variables.
class BaseField3[GT]:
    @overload
    def __new__(
        cls: type[BaseField3[GT]], null: Literal[False] = False, *args: Any, **kwargs: Any
    ) -> BaseField3[GT]: ...
    @overload
    def __new__(
        cls: type[BaseField3[GT]], null: Literal[True], *args: Any, **kwargs: Any
    ) -> BaseField3[GT | None]: ...
    def __new__(cls: Any, null: Any = False, *args: Any, **kwargs: Any) -> Any: ...
    def __get__(self, instance: Any, owner: Any) -> GT: ...


class SpecialField3[GT](BaseField3[GT]):
    ...


class ConcreteCharField3(SpecialField3[str]):
    pass


class User5:
    f1 = ConcreteCharField3(null=False)
    f2 = ConcreteCharField3(null=True)


reveal_type(User5().f1, expected_text="str")
reveal_type(User5().f2, expected_text="str | None")
