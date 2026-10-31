# This sample tests variance inherited from a selected constructor's parameter.

from __future__ import annotations

from typing import Generic, TypeVar


class Animal:
    pass


class Dog(Animal):
    pass


T_co = TypeVar("T_co", covariant=True)
T_inv = TypeVar("T_inv")
T_contra = TypeVar("T_contra", contravariant=True)


class Producer(Generic[T_co]):
    pass


class Box(Generic[T_inv]):
    pass


class Consumer(Generic[T_contra]):
    pass


def accepts_producer[F[X]: Producer[X]](value: F[Animal]) -> None:
    pass


def accepts_box[F[X]: Box[X]](value: F[Animal]) -> None:
    pass


def accepts_consumer[F[X]: Consumer[X]](value: F[Dog]) -> None:
    pass


def accepts_consumer_animal[F[X]: Consumer[X]](value: F[Animal]) -> None:
    pass


accepts_producer(Producer[Dog]())

# This should generate an error because Box is invariant.
accepts_box(Box[Dog]())

accepts_consumer(Consumer[Animal]())

# This should generate an error because Consumer is contravariant.
accepts_consumer_animal(Consumer[Dog]())
