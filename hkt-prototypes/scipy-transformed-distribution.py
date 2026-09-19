# Context: scipy-stubs/stats/_distribution_infrastructure.pyi (lines 1564-1585)
# Reference: https://github.com/jorenham/hkt-survey/blob/main/scipy_transformed_distribution.md
#
# Use case from SciPy:
# `scipy.stats` supports transformed probability distributions (e.g., `exp(X)`, `log(X)`).
# The wrapper `TransformedDistribution` carries the underlying distribution's type constructor `D`
# as a type argument, remembering *which* distribution constructor it transforms while preserving
# the shape parameter `ShapeT`.
#
# Without HKT:
# In standard Python, a class cannot take an unapplied type constructor `D` as a type parameter:
# `class TransformedDistribution[D: Distribution, ShapeT]` fails because `Distribution` is generic,
# and writing `D[ShapeT]` is an invalid subscription of a TypeVar.
# Type stubs were forced to erase the underlying distribution to `Distribution[Any]` or `object`,
# losing all distribution family identity and specialized properties.
#
# With HKT:
# The wrapper carries `D[Sh: tuple[int, ...]]: Distribution[Sh]` as a first-class type constructor parameter:
#     class TransformedDistribution[D[Sh: tuple[int, ...]]: Distribution[Sh], ShapeT: tuple[int, ...]](
#         Distribution[ShapeT]
#     ): ...
# Transform functions `exp` and `log` capture the input constructor `D` and shape `S`:
#     def exp[D[Sh: tuple[int, ...]]: Distribution[Sh], S: tuple[int, ...]](
#         dist: D[S],
#     ) -> TransformedDistribution[D, S]: ...
# - Normal distribution with shape produces `TransformedDistribution[Normal, ...]`.
# - Exponential distribution with shape produces `TransformedDistribution[Exponential, ...]`.
# - Passing a non-Distribution is statically rejected.

from collections.abc import Callable
import math
from typing import reveal_type


class Distribution[ShapeT: tuple[int, ...]]:
    def __init__(self, shape: ShapeT) -> None:
        self.shape = shape

    def sample(self) -> float:
        raise NotImplementedError


class Normal[ShapeT: tuple[int, ...]](Distribution[ShapeT]):
    def __init__(self, shape: ShapeT, mean: float = 0.0, std: float = 1.0) -> None:
        super().__init__(shape)
        self.mean = mean
        self.std = std

    def sample(self) -> float:
        return self.mean


class Exponential[ShapeT: tuple[int, ...]](Distribution[ShapeT]):
    def __init__(self, shape: ShapeT, rate: float = 1.0) -> None:
        super().__init__(shape)
        self.rate = rate

    def sample(self) -> float:
        return 1.0 / self.rate


class TransformedDistribution[D[Sh: tuple[int, ...]]: Distribution[Sh], ShapeT: tuple[int, ...]](
    Distribution[ShapeT]
):
    def __init__(self, base_dist: Distribution[ShapeT], transform_fn: Callable[[float], float], name: str) -> None:
        super().__init__(base_dist.shape)
        self.base_dist = base_dist
        self.transform_fn = transform_fn
        self.name = name

    def sample(self) -> float:
        return self.transform_fn(self.base_dist.sample())


# Mathematical transformation functions capturing the distribution constructor D
def exp[D[Sh: tuple[int, ...]]: Distribution[Sh], S: tuple[int, ...]](
    dist: D[S],
) -> TransformedDistribution[D, S]:
    return TransformedDistribution[D, S](dist, math.exp, "exp")


def log[D[Sh: tuple[int, ...]]: Distribution[Sh], S: tuple[int, ...]](
    dist: D[S],
) -> TransformedDistribution[D, S]:
    return TransformedDistribution[D, S](dist, math.log, "log")


# 1. Base Normal distribution
n = Normal((5,), mean=0.0, std=1.0)
reveal_type(n, expected_text="Normal[tuple[Literal[5]]]")

# 2. Transformed Normal: exp(Normal) -> TransformedDistribution[Normal, ...]
en = exp(n)
reveal_type(en, expected_text="TransformedDistribution[Normal[ShapeT@Normal], tuple[Literal[5]]]")
assert isinstance(en, TransformedDistribution)
assert en.name == "exp"
assert en.sample() == 1.0

# 3. Transformed Exponential: log(Exponential) -> TransformedDistribution[Exponential, ...]
e = Exponential((10,), rate=2.0)
le = log(e)
reveal_type(le, expected_text="TransformedDistribution[Exponential[ShapeT@Exponential], tuple[Literal[10]]]")
assert isinstance(le, TransformedDistribution)
assert le.name == "log"
assert le.sample() == math.log(0.5)
