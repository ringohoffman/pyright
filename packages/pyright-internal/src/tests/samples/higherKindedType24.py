# This sample tests that unsolved higher-kinded type variables in return position
# are cleanly replaced with Unknown rather than leaking raw type variables when
# incompatible non-generic classes are passed as arguments (python/typing#548 comment 843663432).

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, reveal_type


class ObjectId:
    pass


@dataclass
class User:
    __collection__ = "users"
    _id: ObjectId
    username: str


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


# Shadowing: inner constructor dummy param IDT shadows outer function type parameter IDT.
# This should generate an error: TypeVar "IDT" is already in use by an outer scope
def find_one_shadowed[IDT, MongoModelT[IDT]: MongoModel[IDT]](
    model_cls: type[MongoModelT[IDT]], id: IDT
) -> MongoModelT[IDT]:
    raise NotImplementedError


# Clean definition with distinct dummy parameter T:
def find_one[IDT, MongoModelT[T]: MongoModel[T]](
    model_cls: type[MongoModelT[IDT]], id: IDT
) -> MongoModelT[IDT]:
    raise NotImplementedError


# Clean definition with outer template bound:
def find_one_2[IDT, MongoModelT: MongoModel[IDT]](
    model_cls: type[MongoModelT[IDT]], id: IDT
) -> MongoModelT[IDT]:
    raise NotImplementedError


# Generic model matching succeeds:
reveal_type(find_one(SpecialMongoModel, 1), expected_text="SpecialMongoModel[int]")
reveal_type(find_one_2(SpecialMongoModel, 1), expected_text="SpecialMongoModel[int]")

# Non-generic User cannot match higher-kinded MongoModelT[IDT].
# The call generates an error and the return type falls back to Unknown without leaking MongoModelT:
# This should generate an error:
reveal_type(find_one(User, ObjectId()), expected_text="Unknown")
# This should generate an error:
reveal_type(find_one_2(User, ObjectId()), expected_text="Unknown")
