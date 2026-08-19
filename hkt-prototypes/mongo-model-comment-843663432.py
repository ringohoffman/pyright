# https://github.com/python/typing/issues/548#issuecomment-843663432

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, reveal_type

class ObjectId:
    ...


@dataclass
class User:
    __collection__ = "users"  # This is the "table", or collection in Mongo. Class variable, not instance

    @property
    def _id(self) -> ObjectId:
        ...

    username: str  # A random property


class MongoModel[ID](Protocol):
    __collection__: str

    @property
    def _id(self) -> ID:
        ...


class SpecialMongoModel[ID]:
    __collection__: str

    @property
    def _id(self) -> ID:
        ...

class ConcreteUser(MongoModel[ObjectId]):
    __collection__: str = ""

    @property
    def _id(self) -> ObjectId:
        ...


def find_one[IDT, MongoModelT[IDT]: MongoModel[IDT]](model_cls: type[MongoModelT[IDT]], id: IDT) -> MongoModelT[IDT]: ...
def find_one_2[IDT, MongoModelT: MongoModel[IDT]](model_cls: type[MongoModelT[IDT]], id: IDT) -> MongoModelT[IDT]: ...
def find_one_3[MongoModelT[IDT]: MongoModel[IDT]](model_cls: type[MongoModelT[IDT]], id: IDT) -> MongoModelT[IDT]: ...


reveal_type(find_one(SpecialMongoModel, 1), expected_text="SpecialMongoModel[int]")
reveal_type(find_one_2(SpecialMongoModel, 1), expected_text="SpecialMongoModel[int]")

# Note on User and ConcreteUser rejection:
# `find_one_2` declares `MongoModelT` as a higher-kinded type constructor (kind * -> *).
# When matching `model_cls: type[MongoModelT[IDT]]`, `MongoModelT` must be a parameterized
# generic class constructor (like `SpecialMongoModel`) that can be applied to `IDT`.
#
# Even though `User` and `ConcreteUser` structurally conform to `MongoModel[ObjectId]`,
# they are 0-ary (proper) types (kind *), not type constructors. They cannot be applied
# as `User[ObjectId]` or `ConcreteUser[ObjectId]`.
#
# Representing fixed-ID models like `ConcreteUser` alongside generic constructors would
# require associated types / type families (e.g. `M._id`) rather than type constructor application.
reveal_type(find_one_2(User, ObjectId()), expected_text="User")  #  "type[User]" is not a generic type constructor
reveal_type(find_one_2(ConcreteUser, ObjectId()), expected_text="ConcreteUser")  # "MongoModel[ObjectId]" is not a concrete class type and cannot be assigned to type "type[MongoModel[IDT@find_one_2]]"
