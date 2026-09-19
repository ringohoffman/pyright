# https://github.com/python/typing/issues/548#issuecomment-843663432
#
# Use case from Tinche:
# An ODM/ORM querying function `find_one(model_cls, id)` that queries for documents
# based on their model class, preserving the generic model's return type specialized
# to the specific ID type (`SpecialMongoModel[int]`, `Document[ObjectId]`).
#
# Without HKT:
# In standard Python (PEP 484 / PEP 695):
# 1. `find_one(model_cls: type[C], id: ???)` cannot extract the ID type from `C`
#    because Python lacks type deconstruction or associated types.
# 2. Writing `def find_one(model_cls: type[C[TID]], id: TID) -> C[TID]:` fails because
#    `C` is a concrete TypeVar and cannot take arguments ("Type variable used with arguments").
# 3. If `ID` is an independent TypeVar (`def find_one(model_cls: type[C], id: ID)`),
#    Mypy/Pyright treats them independently, so callers can pass mismatched IDs without error.
#
# With HKT:
# The model constructor is declared as a type constructor `MongoModelT[T]: MongoModel[T]`:
#     def find_one[IDT, MongoModelT[T]: MongoModel[T]](
#         model_cls: type[MongoModelT[IDT]], id: IDT
#     ) -> MongoModelT[IDT]:
#         ...
# Passing `find_one(SpecialMongoModel, 123)` cleanly binds `MongoModelT = SpecialMongoModel`
# and `IDT = int`, returning `SpecialMongoModel[int]`.
#
# Note on error cases / misuse guidance:
# When callers pass a non-generic class (e.g. `User`) where a type constructor is required,
# Pyright produces a dedicated diagnostic guiding the user:
#     "type[User]" is not a generic type constructor
# For full error diagnostics and misuse examples, see `hkt-error-cases.py`.

from __future__ import annotations

from typing import Protocol, reveal_type, runtime_checkable


class ObjectId:
    def __init__(self, val: str = "default") -> None:
        self.val = val

    def __repr__(self) -> str:
        return f"ObjectId({self.val!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ObjectId) and self.val == other.val


@runtime_checkable
class MongoModel[ID](Protocol):
    __collection__: str
    _id: ID


class SpecialMongoModel[ID]:
    __collection__: str = "special"

    def __init__(self, id: ID) -> None:
        self._id = id


class Document[ID](MongoModel[ID]):
    __collection__: str = "documents"

    def __init__(self, id: ID, title: str = "untitled") -> None:
        self._id = id
        self.title = title


def find_one[IDT, MongoModelT[T]: MongoModel[T]](
    model_cls: type[MongoModelT[IDT]], id: IDT
) -> MongoModelT[IDT]:
    return model_cls(id)  # pyright: ignore[reportCallIssue]


# 1. Querying SpecialMongoModel with int ID -> SpecialMongoModel[int]
m1 = find_one(SpecialMongoModel, 123)
reveal_type(m1, expected_text="SpecialMongoModel[int]")

# 2. Querying Document with ObjectId -> Document[ObjectId]
oid = ObjectId("abc")
m2 = find_one(Document, oid)
reveal_type(m2, expected_text="Document[ObjectId]")

# 3. Runtime functional validation
assert m1._id == 123  # pyright: ignore[reportPrivateUsage]
assert m1.__collection__ == "special"
assert isinstance(m1, SpecialMongoModel)

assert m2._id == oid  # pyright: ignore[reportPrivateUsage]
assert m2.__collection__ == "documents"
assert isinstance(m2, Document)
assert isinstance(m2, MongoModel)
