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


T = TypeVar("T")
ProducerF = TypeVar("ProducerF", bound=Producer[T])
BoxF = TypeVar("BoxF", bound=Box[T])
ConsumerF = TypeVar("ConsumerF", bound=Consumer[T])
ConsumerAnimalF = TypeVar("ConsumerAnimalF", bound=Consumer[T])


def accepts_producer(value: ProducerF[Animal]) -> None:
    pass


def accepts_box(value: BoxF[Animal]) -> None:
    pass


def accepts_consumer(value: ConsumerF[Dog]) -> None:
    pass


def accepts_consumer_animal(value: ConsumerAnimalF[Animal]) -> None:
    pass


accepts_producer(Producer[Dog]())

# This should generate an error because Box is invariant.
accepts_box(Box[Dog]())

accepts_consumer(Consumer[Animal]())

# This should generate an error because Consumer is contravariant.
accepts_consumer_animal(Consumer[Dog]())


def accepts_producer_pep695[T_inner, F: Producer[T_inner]](value: F[Animal]) -> None:
    pass


def accepts_box_pep695[T_inner, F: Box[T_inner]](value: F[Animal]) -> None:
    pass


def accepts_consumer_pep695[T_inner, F: Consumer[T_inner]](value: F[Dog]) -> None:
    pass


def accepts_consumer_animal_pep695[T_inner, F: Consumer[T_inner]](value: F[Animal]) -> None:
    pass


accepts_producer_pep695(Producer[Dog]())

# This should generate an error because Box is invariant.
accepts_box_pep695(Box[Dog]())

accepts_consumer_pep695(Consumer[Animal]())

# This should generate an error because Consumer is contravariant.
accepts_consumer_animal_pep695(Consumer[Dog]())