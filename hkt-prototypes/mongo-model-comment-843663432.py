# https://github.com/python/typing/issues/548#issuecomment-843663432

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, reveal_type

class ObjectId:
    ...


@dataclass
class User:
    __collection__ = "users"  # This is the "table", or collection in Mongo. Class variable, not instance

    _id: ObjectId  # Every Mongo document has an ID, most often ObjectId, but can be maybe str or something else
    username: str  # A random property


class MongoModel[ID](Protocol):
    __collection__: str

    @property
    def _id(self) -> ID:
        ...


class SpecialMongoModel[ID]:  # structural inherence
    __collection__: str

    @property
    def _id(self) -> ID:
        ...


def find_one[IDT, MongoModelT[IDT]: MongoModel[IDT]](model_cls: type[MongoModelT[IDT]], id: IDT) -> MongoModelT[IDT]: ...
def find_one_2[IDT, MongoModelT: MongoModel[IDT]](model_cls: type[MongoModelT[IDT]], id: IDT) -> MongoModelT[IDT]: ...
def find_one_3[MongoModelT[IDT]: MongoModel[IDT]](model_cls: type[MongoModelT[IDT]], id: IDT) -> MongoModelT[IDT]: ...


reveal_type(find_one(SpecialMongoModel, 1), expected_text="SpecialMongoModel[int]")
reveal_type(find_one_2(SpecialMongoModel, 1), expected_text="SpecialMongoModel[int]")

reveal_type(find_one(User, ObjectId()), expected_text="User")

