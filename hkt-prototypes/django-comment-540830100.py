# https://github.com/python/typing/issues/548#issuecomment-540830100
#
# Use case from syastrov based on Django's ORM `Field`:
# In Django models, fields are defined as class descriptors (e.g. `CharField(null=True)`).
# The descriptor's `__get__` returns the underlying Python type (`str`, `int`, etc.),
# or `type | None` if `null=True`.
#
# Without HKT:
# In standard Python, `Field` cannot specialize its return type in `__new__` across
# subclasses:
#   `@overload def __new__(cls: type[FieldT], null: Literal[True]) -> FieldT[GT | None]`
# fails because `FieldT` is a concrete TypeVar and cannot be applied as `FieldT[GT | None]`.
# Django stubs were forced to require dedicated Mypy/Pyright compiler plugins
# (`django-stubs`) just to synthesize nullable types for fields when `null=True`.
#
# With HKT:
# `Field` defines overloaded constructor specialization once on `__new__`:
# `cls: type[FieldT[GT]] -> FieldT[GT | None]`. Subclasses (`CharField`, `IntegerField`)
# inherit this behavior automatically without plugin magic or redundant overrides.

from __future__ import annotations

from typing import Any, Literal, overload, reveal_type


class Field[GT]:
    def __init__(self, null: bool = False, default: Any = None) -> None:
        self.null = null
        self.default = default
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    # Standard descriptor protocol: instance access returns GT
    def __get__(self, instance: object, owner: Any) -> GT:
        if instance is None:
            return self  # type: ignore
        return getattr(instance, f"_{self.name}", self.default)

    def __set__(self, instance: object, value: GT) -> None:
        setattr(instance, f"_{self.name}", value)

    # HKT constructor specialization on __new__:
    # Instantiating any Field subclass with null=True wraps the inner element type GT -> GT | None
    # while preserving the exact field subclass (CharField, IntegerField, etc.)
    @overload
    def __new__[FieldT: Field[GT]](
        cls: type[FieldT[GT]],
        null: Literal[False] = False,
        *args: Any,
        **kwargs: Any,
    ) -> FieldT[GT]: ...

    @overload
    def __new__[FieldT: Field[GT]](
        cls: type[FieldT[GT]],
        null: Literal[True],
        *args: Any,
        **kwargs: Any,
    ) -> FieldT[GT | None]: ...

    def __new__(cls: Any, *args: Any, **kwargs: Any) -> Any:
        return super().__new__(cls)


class CharField(Field[str]):
    pass


class IntegerField(Field[int]):
    pass


class User:
    username = CharField(null=False)
    bio = CharField(null=True)
    age = IntegerField(null=True)
    score = IntegerField(null=False)


# 1. Non-nullable field instances return non-optional types
reveal_type(User().username, expected_text="str")
reveal_type(User().score, expected_text="int")

# 2. Nullable field instances return Optional types
reveal_type(User().bio, expected_text="str | None")
reveal_type(User().age, expected_text="int | None")

# 3. Runtime functional verification
u = User()
u.username = "alice"
u.bio = None
u.age = 30
u.score = 100

assert u.username == "alice"
assert u.bio is None
assert u.age == 30
assert u.score == 100
