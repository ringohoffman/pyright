# Context: typeshed stubs tensorflow/tensorflow/autodiff.pyi (lines 26-58)
# Reference: https://github.com/jorenham/hkt-survey/blob/main/tensorflow_gradient_tape.md
#
# Use case from TensorFlow:
# `tf.GradientTape.gradient(target, sources)` computes symbolic or numerical gradients of
# `target` with respect to `sources`.
# Crucially, `gradient()` preserves the exact container structure of `sources`:
# - Passing a single `Tensor` returns a single `Gradients` object.
# - Passing a `list[Tensor]` returns `list[Gradients]`.
# - Passing a `set[Tensor]` returns `set[Gradients]`.
# - Passing a `dict[K, Tensor]` returns `dict[K, Gradients]`.
#
# Without HKT:
# In typeshed, maintainers included this explicit comment in `autodiff.pyi`:
#   "# Higher kinded types would be nice here and these overloads are a way to simulate some of them."
# Typeshed was forced to write 4+ manual overloads that compromised on type precision:
# 1. `sources: Sequence[Tensor] -> list[Gradients]`:
#    Erases all non-list sequences (tuples, deques, custom sequence types) to `list`.
# 2. `sources: Mapping[str, Tensor] -> dict[str, Gradients]`:
#    Erases all non-dict mappings (`OrderedDict`, `defaultdict`) to `dict`, and hardcodes
#    the key type to `str` (cannot support `dict[int, Tensor]`).
# 3. `sources: ContainerTensors -> ContainerGradients`:
#    Falls back to a loosely typed union for arbitrary nesting.
#
# With HKT:
# 1. Unary container transmutation:
#    `def gradient[F[T]](self, target: Tensor, sources: F[Tensor]) -> F[Gradients]: ...`
#    Preserves the exact unary container constructor (`list`, `set`, etc.) without type erasure.
# 2. Binary mapping transmutation with key preservation:
#    `def gradient[K, M[Key, Val]: Mapping[Key, Val]](self, target: Tensor, sources: M[K, Tensor]) -> M[K, Gradients]: ...`
#    Preserves both the mapping constructor (`dict`, `OrderedDict`) and arbitrary key types `K`.
# 3. Scalar Tensor overload:
#    `def gradient(self, target: Tensor, sources: Tensor) -> Gradients: ...`
#    Handles uncontained single tensors directly.

from collections import OrderedDict
from collections.abc import Iterable, Mapping
from typing import Any, TypeGuard, cast, overload, reveal_type


class Tensor:
    def __init__(self, name: str = "tensor") -> None:
        self.name = name


class Gradients:
    def __init__(self, source_name: str = "grad") -> None:
        self.source_name = source_name


def is_tensor_mapping[K, M[Key, Val]: Mapping[Key, Val]](val: M[K, Any]) -> TypeGuard[M[K, Tensor]]:
    """Container-preserving HKT TypeGuard narrowing mapping values to Tensors."""
    return all(isinstance(v, Tensor) for v in val.values())


def is_tensor_iterable[F[T]: Iterable[T]](val: F[Any]) -> TypeGuard[F[Tensor]]:
    """Container-preserving HKT TypeGuard narrowing iterable elements to Tensors."""
    return all(isinstance(elem, Tensor) for elem in val)


# In real TensorFlow (tensorflow/python/eager/backprop.py line 1092), this repackaging
# is performed by `tf.nest.pack_sequence_as(sources, flat_grad)`:
#     flat_grad = imperative_grad(...)
#     grad = nest.pack_sequence_as(sources, flat_grad)
#     return grad
# `pack_sequence_as` takes the computed flat list of gradients and reconstructs the
# exact container shape of `sources` (calling `type(structure)(...)`).
def _pack_sequence_as(sources: object, items: Any) -> Any:
    """Minimal reproduction of `tf.nest.pack_sequence_as(structure, flat_sequence)`."""
    ctor: Any = type(sources)
    return ctor(items)


class GradientTape:
    # 1. Unary container transmutation (list[Tensor], set[Tensor], custom containers, etc.)
    @overload
    def gradient[F[T]](self, target: Tensor, sources: F[Tensor]) -> F[Gradients]:
        ...

    # 2. Binary mapping transmutation (dict[K, Tensor], OrderedDict[K, Tensor], etc.)
    @overload
    def gradient[K, M[Key, Val]: Mapping[Key, Val]](
        self, target: Tensor, sources: M[K, Tensor]
    ) -> M[K, Gradients]:
        ...

    # 3. Scalar Tensor -> Gradients
    @overload
    def gradient(self, target: Tensor, sources: Tensor) -> Gradients:
        ...

    def gradient(self, target: Tensor, sources: object) -> object:
        # 1. Scalar Tensor
        if isinstance(sources, Tensor):
            return Gradients(sources.name)

        # 2. Mapping of Tensors: HKT TypeGuard narrows sources while preserving
        # the exact mapping constructor (dict, OrderedDict) and key type K
        if isinstance(sources, Mapping):
            sources_map = cast(Mapping[Any, Any], sources)
            if is_tensor_mapping(sources_map):
                return _pack_sequence_as(
                    sources_map,
                    ((k, Gradients(v.name)) for k, v in sources_map.items()),
                )
            raise TypeError("All mapping values must be Tensors")

        # 3. Iterable of Tensors: HKT TypeGuard narrows sources while preserving
        # the exact container constructor (list, set, tuple, deque)
        if isinstance(sources, Iterable):
            sources_iter = cast(Iterable[Any], sources)
            if is_tensor_iterable(sources_iter):
                return _pack_sequence_as(
                    sources_iter,
                    (Gradients(elem.name) for elem in sources_iter),
                )
            raise TypeError("All iterable elements must be Tensors")

        raise TypeError(f"Unsupported sources type: {type(sources)}")


tape = GradientTape()
t = Tensor("x")

# 1. Scalar Tensor -> Gradients
r0 = tape.gradient(t, t)
reveal_type(r0, expected_text="Gradients")

# 2. list[Tensor] -> list[Gradients]
xs: list[Tensor] = [Tensor("x1"), Tensor("x2")]
r1 = tape.gradient(t, xs)
reveal_type(r1, expected_text="list[Gradients]")

# 3. set[Tensor] -> set[Gradients] (typeshed would have erased this to list)
s: set[Tensor] = {t}
r2 = tape.gradient(t, s)
reveal_type(r2, expected_text="set[Gradients]")

# 4. dict[str, Tensor] -> dict[str, Gradients]
d: dict[str, Tensor] = {"w1": Tensor("w1")}
r3 = tape.gradient(t, d)
reveal_type(r3, expected_text="dict[str, Gradients]")

# 5. OrderedDict[int, Tensor] -> OrderedDict[int, Gradients]
# Preserves non-str keys (int) and concrete mapping class (OrderedDict)
od: OrderedDict[int, Tensor] = OrderedDict([(1, Tensor("layer1"))])
r4 = tape.gradient(t, od)
reveal_type(r4, expected_text="OrderedDict[int, Gradients]")

# 6. Container-preserving TypeGuard: narrows list[object] -> list[Tensor] -> list[Gradients]
raw_list: list[object] = [Tensor("u1"), Tensor("u2")]
if is_tensor_iterable(raw_list):
    reveal_type(raw_list, expected_text="list[Tensor]")
    r5 = tape.gradient(t, raw_list)
    reveal_type(r5, expected_text="list[Gradients]")
    assert len(r5) == 2 and isinstance(r5, list)

# 7. Container-preserving TypeGuard: narrows dict[str, object] -> dict[str, Tensor] -> dict[str, Gradients]
raw_dict: dict[str, object] = {"k": Tensor("uk")}
if is_tensor_mapping(raw_dict):
    reveal_type(raw_dict, expected_text="dict[str, Tensor]")
    r6 = tape.gradient(t, raw_dict)
    reveal_type(r6, expected_text="dict[str, Gradients]")
    assert isinstance(r6, dict) and isinstance(r6["k"], Gradients)

# 8. Runtime functional assertions
assert isinstance(r0, Gradients)
assert r0.source_name == "x"

assert isinstance(r1, list)
assert len(r1) == 2 and all(isinstance(g, Gradients) for g in r1)

assert isinstance(r2, set)
assert len(r2) == 1 and all(isinstance(g, Gradients) for g in r2)

assert isinstance(r3, dict)
assert isinstance(r3["w1"], Gradients)

assert isinstance(r4, OrderedDict)
assert isinstance(r4[1], Gradients)
