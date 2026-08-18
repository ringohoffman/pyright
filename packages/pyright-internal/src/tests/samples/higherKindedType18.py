# This sample tests constructor variance: subtyping across generic container types
# (covariance and contravariance in container hierarchies).

from __future__ import annotations

from typing import TypeVar, reveal_type


class Animal:
    pass


class Dog(Animal):
    pass


# Covariant container family
class BaseProducer[T]:
    pass


class SubProducer[T](BaseProducer[T]):
    pass


# Contravariant / sink container family
class BaseSink[T]:
    pass


class SpecificSink[T](BaseSink[T]):
    pass


class UnrelatedContainer[T]:
    pass


# Case 1: PEP 695 producer container constructor variance
def process_producer[T, F: BaseProducer[T], U](
    value: F[T], new_val_type: type[U]
) -> F[U]:
    raise NotImplementedError


# 1a. Passing SubProducer preserves SubProducer in return type (constructor identity invariance)
sub1 = process_producer(SubProducer[Dog](), str)
reveal_type(sub1, expected_text="SubProducer[str]")

# 1b. Passing BaseProducer preserves BaseProducer in return type
base1 = process_producer(BaseProducer[Dog](), str)
reveal_type(base1, expected_text="BaseProducer[str]")

# 1c. Passing UnrelatedContainer violates container bound BaseProducer[T]
# This should generate an error because UnrelatedContainer does not derive from BaseProducer.
process_producer(UnrelatedContainer[Dog](), str)


# Case 2: Sink container constructor variance
def process_sink[T, F: BaseSink[T], U](
    value: F[T], new_val_type: type[U]
) -> F[U]:
    raise NotImplementedError


sink1 = process_sink(SpecificSink[Animal](), int)
reveal_type(sink1, expected_text="SpecificSink[int]")

# This should generate an error because UnrelatedContainer does not derive from BaseSink.
process_sink(UnrelatedContainer[Animal](), int)


# Case 3: Legacy TypeVar container constructor variance
T_legacy = TypeVar("T_legacy")
U_legacy = TypeVar("U_legacy")
F_legacy = TypeVar("F_legacy", bound=BaseProducer[T_legacy])


def process_producer_legacy(
    value: F_legacy[T_legacy], new_val_type: type[U_legacy]
) -> F_legacy[U_legacy]:
    raise NotImplementedError


sub2 = process_producer_legacy(SubProducer[Dog](), str)
reveal_type(sub2, expected_text="SubProducer[str]")

base2 = process_producer_legacy(BaseProducer[Dog](), str)
reveal_type(base2, expected_text="BaseProducer[str]")

# This should generate an error because UnrelatedContainer does not derive from BaseProducer.
process_producer_legacy(UnrelatedContainer[Dog](), str)
