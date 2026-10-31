# PEP [XXXX]: Type Constructor Parameters

- **Author**: Matthew Hoffman <ringohoffman at me.com>
- **Sponsor**: 
- **Discussions-To**:
- **Status**: Draft
- **Type**: Standards Track
- **Topic**: Typing
- **Created**: 19-Sep-2026
- **Python-Version**: 3.16
- **Post-History**: 
- **Resolution**: 

---

## Abstract

This PEP extends the type parameter syntax introduced in [PEP 695](https://peps.python.org/pep-0695) to support type constructor parameters (higher-kinded type parameters). A generic class, function, or type alias may declare a type parameter that ranges over type constructors rather than types, allowing type checkers to preserve both a container and its type arguments through generic code.

## Motivation

A common use case is a method on a generic class that returns a new instance of the same class with different type arguments. The standard library's `dict.fromkeys` is such a method: it constructs a mapping whose key type comes from the `iterable` argument, whose value type comes from the `value` argument, and whose class comes from `cls`.

```python
from collections import defaultdict

defaultdict.fromkeys(["a", "b"], 0)  # => dict[str, int]
```

The type checker infers `dict[str, int]` rather than `defaultdict[str, int]`. The subclass is lost, because the stub for `fromkeys` can only name a concrete class in its return type:

```python
class dict[KT, VT]:
    @classmethod
    def fromkeys[T, S](cls, iterable: Iterable[T], value: S, /) -> dict[T, S]: ...
```

[PEP 673](https://peps.python.org/pep-0673) introduced `Self` for methods that return an instance of the current class. It does not help here. `Self` stands for the current class *with its current type arguments*, but `fromkeys` must supply new ones:

```python
class dict[KT, VT]:
    @classmethod
    def fromkeys[T, S](cls, iterable: Iterable[T], value: S, /) -> Self: ...

defaultdict.fromkeys(["a", "b"], 0)  # => defaultdict[Unknown, Unknown]
```

Now the class is preserved but the key and value types are lost.

The present workaround is for every subclass to redeclare the method with its own name in the return type. typeshed does this by hand for `OrderedDict`, `UserDict`, and `ChainMap`:

```python
class OrderedDict[KT, VT](dict[KT, VT]):
    @classmethod
    def fromkeys[T, S](cls, iterable: Iterable[T], value: S) -> OrderedDict[T, S]: ...
```

It has not done so for `defaultdict`, and user-defined subclasses of `dict` almost never do so at all. What is needed is a way to write "the class of `cls`, whatever it is, applied to `T` and `S`". That requires a type parameter that ranges over the *class* rather than over a type:

```python
class dict[KT, VT]:
    @classmethod
    def fromkeys[T, S, D: dict[T, S]](cls: type[D[T, S]], iterable: Iterable[T], value: S, /) -> D[T, S]: ...

defaultdict.fromkeys(["a", "b"], 0)   # => defaultdict[str, int]
OrderedDict.fromkeys(["a", "b"], 0)   # => OrderedDict[str, int]
```

`D` is a *type constructor parameter*. It is solved to the unapplied class `defaultdict`, and `D[T, S]` applies that class to the inferred key and value types. No subclass needs to redeclare `fromkeys`.

The same limitation appears whenever a method must return the receiver's class with its type arguments rearranged. The `bidict` library's `inverse` returns a mapping of the same class with keys and values swapped:

```python
class BidirectionalMapping[KT, VT](Mapping[KT, VT]):
    def inverse[M: BidirectionalMapping[KT, VT]](self: M[KT, VT]) -> M[VT, KT]: ...

bidict({"a": 1}).inverse  # => bidict[int, str]
```

Type constructor parameters are also useful on classes, where a class is generic over the container its methods produce; these cases are surveyed in [Appendix B](#appendix-b-survey-of-real-world-python-use-cases).

### Evidence from the Standard Library

The limitation described above is not an edge case confined to third-party abstractions; it affects the most fundamental container hierarchies in Python's standard library. An audit of standard library stubs in typeshed reveals two recurring problems:

1. **Subclass type erasure**: When a base class method returns a container whose type parameters depend on method arguments, the stub must hardcode the base class. Subclasses that inherit the method without re-declaring it suffer silent type erasure at call sites, even when CPython's runtime implementation correctly constructs and returns an instance of the subclass:
   - `dict.fromkeys`: Inherited by standard library subclasses (`collections.defaultdict`, `http.cookies.SimpleCookie`, `enum._EnumDict`, `logging.config.ConvertingDict`) and 78 verified third-party subclasses across packages such as `docker`, `geojson`, and `Authlib`. At runtime, `SimpleCookie.fromkeys(...)` returns `SimpleCookie`, but type checkers infer `dict`.
   - `collections.abc.Set` operators (`__or__`, `__and__`, `__sub__`, `__xor__`) and `_from_iterable`: In CPython (`_collections_abc.py`), `Set` implements `__or__` as `return self._from_iterable(...)`, where `_from_iterable` is a `@classmethod` constructor hook that instantiates `cls`. Subclasses like `IntSet([1, 2])` preserve their runtime type on union (`s1 | {3, 4}` evaluates to `IntSet`). However, typeshed routes `collections.abc.Set` to `typing.AbstractSet` (via `from typing import AbstractSet as Set` in `_collections_abc.pyi`), where `__or__` hardcodes `-> AbstractSet[_T_co | _T]`, erasing every subclass to `AbstractSet`.

2. **Manual stub duplication**: To prevent this erasure, typeshed authors have hand-duplicated method signatures across subclasses:
   - `fromkeys` is manually re-declared in `OrderedDict`, `UserDict`, and `ChainMap`.
   - `__or__` and `__ror__` overloads are duplicated across `OrderedDict`, `defaultdict`, `UserDict`, and `ChainMap` (12 distinct overload definitions in `collections/__init__.pyi` alone).
   - This duplication protects only immediate standard library subtypes that typeshed authors maintain by hand; any user-defined subclass of `defaultdict` or `OrderedDict` loses its subclass identity when calling these operators.

<table>
  <thead>
    <tr>
      <th>Operation Family</th>
      <th>Base Protocol / Class</th>
      <th>Method</th>
      <th>Current Typeshed Return</th>
      <th>Subclass Runtime Return</th>
      <th>Consequence in Typeshed Today</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="10"><strong>Mapping Constructor Classmethods</strong><br>(<code>fromkeys</code>)</td>
      <td><code>builtins.dict</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/builtins.pyi#L1331-L1336"><code>@classmethod fromkeys(iterable, value)</code></a></td>
      <td><code>dict[_T, _S]</code></td>
      <td>Base mapping factory</td>
      <td><strong>Source of erasure</strong>: Base return type cannot be parameterized by subclass constructor.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/collections/__init__.pyi#L441"><code>collections.defaultdict</code></a></td>
      <td>Inherited from <code>dict.fromkeys</code></td>
      <td><code>dict[_T, _S]</code></td>
      <td><code>defaultdict</code></td>
      <td><strong>Silent erasure</strong>: Factory call drops default factory and subclass identity.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/http/cookies.pyi#L46"><code>http.cookies.BaseCookie</code></a></td>
      <td>Inherited from <code>dict.fromkeys</code></td>
      <td><code>dict[_T, _S]</code></td>
      <td><code>BaseCookie</code></td>
      <td><strong>Silent erasure</strong>: Generic cookie container drops parameterization and subclass identity.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/http/cookies.pyi#L57"><code>http.cookies.SimpleCookie</code></a></td>
      <td>Inherited from <code>dict.fromkeys</code></td>
      <td><code>dict[_T, _S]</code></td>
      <td><code>SimpleCookie</code></td>
      <td><strong>Silent erasure</strong>: Cookie mapping API (<code>output</code>, <code>value_decode</code>) is lost at call sites.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/enum.pyi#L69"><code>enum._EnumDict</code></a></td>
      <td>Inherited from <code>dict.fromkeys</code></td>
      <td><code>dict[_T, _S]</code></td>
      <td><code>_EnumDict</code></td>
      <td><strong>Silent erasure</strong>: Enum member mapping namespace erases to plain <code>dict</code>.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/logging/config.pyi#L81"><code>logging.config.ConvertingDict</code></a></td>
      <td>Inherited from <code>dict.fromkeys</code></td>
      <td><code>dict[_T, _S]</code></td>
      <td><code>ConvertingDict</code></td>
      <td><strong>Silent erasure</strong>: Configuration conversion helpers are lost at call sites.</td>
    </tr>
    <tr>
      <td><code>builtins.frozendict</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/builtins.pyi#L1402-L1407"><code>@classmethod fromkeys(iterable, value)</code></a></td>
      <td><code>frozendict[_T, _S]</code></td>
      <td>Returns subclass (<code>SubFrozenDict</code>)</td>
      <td><strong>Silent erasure</strong>: All subclasses erase to <code>frozendict</code>.</td>
    </tr>
    <tr>
      <td><code>collections.OrderedDict</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/collections/__init__.pyi#L394-L399"><code>@classmethod fromkeys(iterable, value)</code></a></td>
      <td><code>OrderedDict[_T, _S]</code></td>
      <td>Returns subclass (<code>SubOrderedDict</code>)</td>
      <td><strong>Manual duplication</strong>: Hand-duplicated in <code>collections/__init__.pyi</code>.</td>
    </tr>
    <tr>
      <td><code>collections.UserDict</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/collections/__init__.pyi#L89-L94"><code>@classmethod fromkeys(iterable, value)</code></a></td>
      <td><code>UserDict[_T, _S]</code></td>
      <td>Returns subclass (<code>MyUserDict</code>)</td>
      <td><strong>Manual duplication</strong>: Hand-duplicated in <code>collections/__init__.pyi</code>.</td>
    </tr>
    <tr>
      <td><code>collections.ChainMap</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/collections/__init__.pyi#L536-L549"><code>@classmethod fromkeys(iterable, value)</code></a></td>
      <td><code>ChainMap[_T, _S]</code></td>
      <td>Returns subclass</td>
      <td><strong>Manual duplication</strong>: Hand-duplicated in <code>collections/__init__.pyi</code>.</td>
    </tr>
    <tr>
      <td><strong>Immutable Mapping Instantiation</strong><br>(<code>__new__</code>)</td>
      <td><code>builtins.frozendict</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/builtins.pyi#L1383-L1398"><code>__new__(cls, ...)</code></a></td>
      <td><code>frozendict[_KT, _VT]</code></td>
      <td>Returns subclass with inferred key/value types</td>
      <td><strong>Silent erasure</strong>: Constructor cannot use <code>Self</code> to infer new type arguments, erasing all subclasses to <code>frozendict</code>.</td>
    </tr>
    <tr>
      <td rowspan="2"><strong>Set Construction &amp; Algebra</strong><br>(<code>collections.abc.Set</code>)</td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/_collections_abc.pyi#L5"><code>collections.abc.Set</code></a><br>(as <code>typing.AbstractSet</code>)</td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/typing.pyi#L737-L738"><code>@classmethod _from_iterable(it)</code></a></td>
      <td><code>AbstractSet[_S]</code></td>
      <td>Returns subclass (<code>IntSet</code>, <code>KeysView</code>, <code>ItemsView</code>, <code>WeakSet</code>)</td>
      <td><strong>Silent erasure</strong>: Erases custom sets to <code>AbstractSet</code>.</td>
    </tr>
    <tr>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/_collections_abc.pyi#L5"><code>collections.abc.Set</code></a><br>(as <code>typing.AbstractSet</code>)</td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/typing.pyi#L743-L746"><code>__or__</code>, <code>__and__</code>, <code>__sub__</code>, <code>__xor__</code></a></td>
      <td><code>AbstractSet[_T_co | _T]</code></td>
      <td>Returns subclass (<code>IntSet</code>, etc.) via <code>_from_iterable</code></td>
      <td><strong>Silent erasure</strong>: Set algebra erases to <code>AbstractSet</code>.</td>
    </tr>
    <tr>
      <td rowspan="5"><strong>Mapping Union Operators</strong><br>(<code>|</code>, <code>__or__</code> / <code>__ror__</code>)</td>
      <td><code>builtins.frozendict</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/builtins.pyi#L1425-L1430"><code>__or__</code>, <code>__ror__</code></a></td>
      <td><code>frozendict[_KT | _T1, _VT | _T2]</code></td>
      <td>Returns subclass (<code>SubFrozenDict</code>)</td>
      <td><strong>Silent erasure</strong>: All subclasses erase to <code>frozendict</code>.</td>
    </tr>
    <tr>
      <td><code>collections.defaultdict</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/collections/__init__.pyi#L484-L492"><code>__or__</code>, <code>__ror__</code></a></td>
      <td><code>defaultdict[_KT | _T1, _VT | _T2]</code></td>
      <td>Returns subclass (<code>SubDefaultDict</code>)</td>
      <td><strong>Manual duplication</strong>: Hand-duplicated 3 times in <code>collections/__init__.pyi</code>; erases further subclasses.</td>
    </tr>
    <tr>
      <td><code>collections.OrderedDict</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/collections/__init__.pyi#L418-L438"><code>__or__</code>, <code>__ror__</code></a></td>
      <td><code>OrderedDict[_KT | _T1, _VT | _T2]</code></td>
      <td>Returns subclass (<code>SubOrderedDict</code>)</td>
      <td><strong>Manual duplication</strong>: Hand-duplicated 4 times in <code>collections/__init__.pyi</code>; erases further subclasses.</td>
    </tr>
    <tr>
      <td><code>collections.ChainMap</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/collections/__init__.pyi#L551-L559"><code>__or__</code>, <code>__ror__</code></a></td>
      <td><code>ChainMap[_KT | _T1, _VT | _T2]</code></td>
      <td>Returns subclass</td>
      <td><strong>Manual duplication</strong>: Hand-duplicated 4 times in <code>collections/__init__.pyi</code>; erases further subclasses.</td>
    </tr>
    <tr>
      <td><code>collections.UserDict</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/collections/__init__.pyi#L96-L104"><code>__or__</code>, <code>__ror__</code></a></td>
      <td><code>UserDict[_KT | _T1, _VT | _T2]</code></td>
      <td>Returns subclass (<code>MyUserDict</code>)</td>
      <td><strong>Manual duplication</strong>: Hand-duplicated in <code>collections/__init__.pyi</code>; erases further subclasses.</td>
    </tr>
    <tr>
      <td rowspan="2"><strong>Container Structure &amp; Element Widening</strong><br>(<code>new_child</code>, <code>+</code>)</td>
      <td><code>collections.ChainMap</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/collections/__init__.pyi#L497"><code>new_child(m)</code></a></td>
      <td><code>Self</code> (requires identical <code>KT, VT</code>)</td>
      <td>Returns <code>ChainMap</code> with widened key/value types</td>
      <td><strong>Type restriction</strong>: Cannot type prepending mappings with new key/value types without losing subclass.</td>
    </tr>
    <tr>
      <td><code>collections.UserList</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stdlib/collections/__init__.pyi#L148-L149"><code>__add__</code>, <code>__radd__</code></a></td>
      <td><code>Self</code> (requires identical <code>_T</code>)</td>
      <td>Returns subclass (<code>MyUserList</code>) with widened item types</td>
      <td><strong>Type restriction</strong>: Cannot type concatenation with new element types without losing subclass.</td>
    </tr>
  </tbody>
</table>

### Evidence from the Ecosystem

The same structural limitation appears whenever third-party frameworks combine class inheritance with generic transformations. Demand for a solution has been tracked in [python/typing issue 548](https://github.com/python/typing/issues/548) since March 2018, accumulating over 220 comments from 60 participants. 

In multiple flagship libraries and stub repositories, maintainers have left explicit comments in their source stubs explaining that higher-kinded type constructor parameters are the missing primitive forcing their current compromises.

<table>
  <thead>
    <tr>
      <th>Operation Family</th>
      <th>Package &amp; Class</th>
      <th>Method / Pattern</th>
      <th>Current Typing in Stubs</th>
      <th>Desired / Runtime Behavior</th>
      <th>Consequence in Ecosystem Today</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2"><strong>Array &amp; Buffer Transmutation</strong></td>
      <td><strong>NumPy</strong><br><code>numpy.ndarray</code></td>
      <td><a href="https://github.com/numpy/numpy/blob/a98529dfd92d73fd4d40ebaaf285cf2463bb92b1/numpy/__init__.pyi#L6670-L6675"><code>view(type=SubClass, dtype=...)</code></a></td>
      <td>Special-cased overloads for <code>memmap</code>, <code>recarray</code>, <code>MaskedArray</code></td>
      <td>Preserves array subclass constructor (<code>SubClass[Shape, NewDType]</code>)</td>
      <td><strong>Commented in NumPy stubs</strong>: <a href="https://github.com/numpy/numpy/blob/a98529dfd92d73fd4d40ebaaf285cf2463bb92b1/numpy/__init__.pyi#L6670-L6671"><i>"NOTE: Python has no support for higher-kinded types, so we special-case some known array subclasses to avoid erasing the shape-type and dtype."</i></a> Third-party array subclasses erase to base <code>ndarray</code>.</td>
    </tr>
    <tr>
      <td><strong>SciPy</strong><br><code>scipy.sparse._spbase</code></td>
      <td><a href="https://github.com/scipy/scipy-stubs/blob/master/scipy-stubs/sparse/_base.pyi#L1031-L1040"><code>astype(dtype=...)</code></a></td>
      <td>14 manual per-subclass overloads in <code>scipy-stubs</code></td>
      <td>Preserves sparse matrix subclass constructor (<code>csr_array</code>, <code>csc_array</code>, etc.) across heterogeneous arities</td>
      <td><strong>Massive stub duplication</strong>: 14 duplicated overloads in <code>_base.pyi</code>; third-party sparse subclasses are not typed.</td>
    </tr>
    <tr>
      <td rowspan="3"><strong>Container &amp; Tree Transmutation</strong></td>
      <td><strong>TensorFlow</strong><br><code>tf.GradientTape</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stubs/tensorflow/tensorflow/autodiff.pyi#L26-L35"><code>gradient(target, sources: F[Tensor])</code></a></td>
      <td>Hardcoded overloads for <code>Tensor</code>, <code>list</code>, <code>dict</code>, <code>tuple</code></td>
      <td>Returns exact container structure <code>F[Gradients]</code> for any container <code>F</code></td>
      <td><strong>Commented in typeshed stubs</strong>: <a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stubs/tensorflow/tensorflow/autodiff.pyi#L26"><i>"Higher kinded types would be nice here and these overloads are a way to simulate some of them."</i></a> Custom containers erase to list/tuple.</td>
    </tr>
    <tr>
      <td><strong>Google JAX</strong><br><code>jax.tree_util</code></td>
      <td><a href="https://github.com/google/jax/blob/main/jax/_src/tree_util.py#L395-L398"><code>tree_map(f, tree, *rest)</code></a></td>
      <td><a href="https://github.com/google/jax/blob/main/jax/_src/tree_util.py#L40"><code>PyTree = Any</code></a>; return type typed as <code>-> Any</code></td>
      <td>Preserves nested container structure <code>Tree[T] -> Tree[U]</code> across arbitrary dicts, lists, tuples, and custom nodes</td>
      <td><strong>Universal type erasure</strong>: JAX's core tree-mapping primitive cannot parameterize over container structure, completely dropping static typing for return values to <code>Any</code>.</td>
    </tr>
    <tr>
      <td><strong>PyTorch</strong><br><code>torch.utils._pytree</code></td>
      <td><a href="https://github.com/pytorch/pytorch/blob/main/torch/utils/_pytree.py#L1559-L1564"><code>tree_map(func, tree, *rests)</code></a></td>
      <td><a href="https://github.com/pytorch/pytorch/blob/main/torch/utils/_pytree.py#L133"><code>PyTree = Any</code></a>; return type typed as <code>-> PyTree</code> (<code>Any</code>)</td>
      <td>Preserves nested container structure <code>Tree[T] -> Tree[U]</code> across tensor trees</td>
      <td><strong>Universal type erasure</strong>: PyTorch cannot parameterize the tree structure over leaf tensor types; all tree operations erase structure to <code>Any</code>.</td>
    </tr>
    <tr>
      <td rowspan="2"><strong>Framework Descriptors &amp; Decorators</strong></td>
      <td><strong>Django ORM</strong><br><code>django.db.models.Field</code></td>
      <td><a href="https://github.com/typeddjango/django-stubs/blob/master/django-stubs/db/models/fields/__init__.pyi#L57-L60"><code>Field[SetType, GetType]</code></a><br>(<a href="https://github.com/typeddjango/django-stubs/blob/master/mypy_django_plugin/transformers/fields.py#L137-L161">plugin hook</a>)</td>
      <td>Synthesized via dedicated <code>django-stubs</code> Mypy plugin</td>
      <td>Specializes descriptor return type across subclasses to <code>FieldT[T | None]</code> when <code>null=True</code></td>
      <td><strong>Compiler plugin dependency</strong>: Stubs cannot express nullable field transmutation in pure typing; required a dedicated AST transformer plugin in Mypy (<a href="https://github.com/python/typing/issues/548#issuecomment-540830100">python/typing#548 (comment)</a>).</td>
    </tr>
    <tr>
      <td><strong>Django Admin</strong><br><code>@admin.register(Model)</code></td>
      <td><a href="https://github.com/typeddjango/django-stubs/blob/master/django-stubs/contrib/admin/decorators.pyi#L68-L70"><code>@register(Model)</code> on <code>ModelAdmin[Model]</code></a></td>
      <td>Ordinary <code>_ModelAdmin = TypeVar("_ModelAdmin", bound=ModelAdmin[Any])</code></td>
      <td>Enforces cross-parameter consistency between model and <code>AdminT[Model]</code></td>
      <td><strong>Loss of type safety</strong>: Cannot verify at decoration time that the registered model matches the admin's generic argument (<a href="https://github.com/typeddjango/django-stubs/issues/3387">django-stubs#3387</a>).</td>
    </tr>
    <tr>
      <td><strong>ORM Expression Flattening</strong></td>
      <td><strong>SQLAlchemy</strong><br><code>sqlalchemy.sql.ColumnElement</code></td>
      <td><a href="https://github.com/sqlalchemy/sqlalchemy/issues/7519"><code>ColumnElement[TypeEngine[T]]</code></a></td>
      <td>Compromised to flattened <code>ColumnElement[T]</code> in <code>sqlalchemy2-stubs</code></td>
      <td>Encapsulates column expression wrappers over database type engines</td>
      <td><strong>Documented hierarchy compromise</strong>: Author Mike Bayer <a href="https://github.com/python/typing/issues/548#issuecomment-1003624963">testified</a> that SQLAlchemy 2.0 typing was forced to break its class hierarchy because HKT was missing.</td>
    </tr>
    <tr>
      <td rowspan="2"><strong>Class-Level Constructor Abstraction</strong></td>
      <td><strong>Gevent</strong><br><code>gevent.pool.Group</code></td>
      <td><a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stubs/gevent/gevent/pool.pyi#L166-L175"><code>Group[G[T]]</code></a></td>
      <td>Non-generic in greenlet type (erases to <code>Greenlet[..., Any]</code>)</td>
      <td>Parameterizes group over greenlet constructor <code>G</code> while allowing mixed return types in the pool</td>
      <td><strong>Commented in typeshed stubs</strong>: <a href="https://github.com/python/typeshed/blob/a767999081c11a6038300ad7a326900c5447ae1b/stubs/gevent/gevent/pool.pyi#L166-L170"><i>"We would need higher-kinded TypeVars if we wanted to give up neither... and keep spawn/apply return types specific."</i></a></td>
    </tr>
    <tr>
      <td><strong>SciPy Stats</strong><br><code>TransformedDistribution</code></td>
      <td><a href="https://github.com/scipy/scipy-stubs/blob/master/scipy-stubs/stats/_distribution_infrastructure.pyi#L1595-L1605"><code>TransformedDistribution[DistT, FloatT, ShapeT]</code></a></td>
      <td>Tied to concrete distribution base class with redundant type parameters</td>
      <td>Carries distribution constructor <code>D</code> (e.g. <code>Normal</code>, <code>Exponential</code>) as type argument</td>
      <td><strong>Loss of domain identity</strong>: Mathematical transformations lose the underlying distribution constructor and specialized properties.</td>
    </tr>
    <tr>
      <td><strong>Subclass Self-Permutation</strong></td>
      <td><strong>bidict</strong><br><code>BidirectionalMapping</code></td>
      <td><a href="https://github.com/jab/bidict/blob/main/bidict/_abc.py#L40-L45"><code>.inverse</code> property</a></td>
      <td>Hardcoded base <code>BidirectionalMapping[VT, KT]</code> return type</td>
      <td>Returns same subclass with swapped type parameters (<code>M[VT, KT]</code>)</td>
      <td><strong>Limitation of PEP 673 <code>Self</code></strong>: Inherited <code>inverse</code> call on <code>frozenbidict</code> or <code>OrderedBidict</code> erases subclass identity to base (<a href="https://github.com/python/typing/issues/548#issuecomment-621195693">python/typing#548 (comment)</a>).</td>
    </tr>
  </tbody>
</table>

Detailed code walkthroughs for each of these use cases appear in [Appendix B](#appendix-b-survey-of-real-world-python-use-cases).

## Summary Examples

## Terminology

### Proper Types (Kind ∗)

A **kind** classifies a type the way a type classifies a value. A **proper type** is a type of kind ∗ (read as "star"): any complete type that can annotate a value.

```python
x: int                     # ∗
y: str | None              # ∗
z: list[int]               # ∗
def f[T](v: T) -> T: ...   # T is ∗
```

### Unary Type Constructors (Kind ∗→∗)

A **unary type constructor** takes one proper type and returns a proper type. Its kind is ∗→∗ (read as "star to star"), operating as a function signature at the type level.

```python
list                # ∗→∗
list[int]           # ∗

Iterable            # ∗→∗
Iterable[str]       # ∗

class Box[T]: ...   # Box is ∗→∗
Box[bytes]          # ∗
```

Supplying a constructor's arguments is **application**: `list[int]` is `list` **applied** to `int`, and has kind ∗. Bare `list` is **unapplied**: it still has kind ∗→∗ and is not a proper type.

### Binary Type Constructors (Kind ∗→∗→∗)

A **binary type constructor** takes two proper types and returns a proper type. Its kind is ∗→∗→∗ (read as "star to star to star").

```python
dict                        # ∗→∗→∗
dict[str, int]              # ∗

Mapping                     # ∗→∗→∗
Mapping[str, bytes]         # ∗

class Pair[K, V]: ...       # Pair is ∗→∗→∗
Pair[str, int]              # ∗
```

### Partially Applied Type Constructors

A **partially applied type constructor** fixes some arguments of a higher-arity constructor, creating a constructor of lower arity.

```python
dict                              # ∗→∗→∗
type StrDict[V] = dict[str, V]    # StrDict is ∗→∗
StrDict[int]                      # ∗  (dict[str, int])
```

### Type Constructor Parameters

A **type constructor parameter** (higher-kinded type parameter) is a type parameter that ranges over type constructors instead of proper types. It is declared either by subscripting its name (`F[T]`) or by bounding it with a class applied to type variables already in scope (`D: dict[T, S]`).

```python
def ident[T](x: T) -> T: ...                              # T ranges over ∗:    int, list[str], ...
def swap[F[T]](x: F[int]) -> F[str]: ...                  # F ranges over ∗→∗:  list, set, Iterable, ...
def keep[K, V, D: dict[K, V]](x: D[K, V]) -> D[K, V]: ... # D ranges over ∗→∗→∗ subclasses of dict

swap([1, 2])                   # F = list,        returns list[str]
swap({1, 2})                   # F = set,         returns set[str]
keep(OrderedDict({"a": 1}))    # D = OrderedDict, returns OrderedDict[str, int]
```

The `T` in `F[T]` is an inner type parameter of `F`, not a type parameter of `swap`. The `K` and `V` in `D: dict[K, V]` are ordinary type parameters of `keep`; their appearance in the bound is what makes `D` a type constructor parameter.

### Inner Type Parameters and Arity

The **arity** of a type constructor is the number of arguments it takes. An **inner type parameter** is a parameter declared inside the brackets of a type constructor parameter; it declares arity and may carry bounds or constraints that restrict valid applications.

```python
def f[F[T]](x: F[int]) -> F[str]: ...                     # F has arity 1  (∗→∗)
def g[M[K, V]](x: M[str, int]) -> M[int, str]: ...        # M has arity 2  (∗→∗→∗)

def h[F[X: int]: IntBox[X]](x: F[str]) -> None: ...      # error: str violates bound on X
def bad[F[T]: Functor[Any]](x: F[int]) -> None: ...       # error: T is unused in bound
```

Inner type parameters are in scope only within their constructor parameter's declaration, bounds, and defaults; they are invisible to the signature and the enclosing body. When a bound or constraint is specified, every inner parameter must appear in it.

### Higher-Order Type Constructors (Kind (∗→∗)→∗)

A **higher-order type constructor** (higher-kinded type) is a generic class or alias declared with a type constructor parameter: it takes a type constructor and returns a proper type. Its kind is (∗→∗)→∗ (read as "star-to-star to star").

```python
class Batch[F[T]]:      # Batch is (∗→∗)→∗
    ints: F[int]
    strs: F[str]

Batch[list]             # ∗  (ints: list[int], strs: list[str])
Batch[set]              # ∗  (ints: set[int],  strs: set[str])
Batch[int]              # error: int is ∗, not ∗→∗
```

This is the one location where a bare constructor such as `list` is a valid type argument.

### Eta-Reduction

**Eta-reduction** (η-reduction) reads a constructor applied to exactly its own inner parameters, in order, as the bare constructor: over inner parameter `T`, `list[T]` means `list`.

```python
class Group[G[T]: Greenlet[T] = Greenlet[T]]: ...   # bound Greenlet, default Greenlet
class Group[G[T]: Greenlet[T] = Greenlet]: ...      # equivalent

class Cfg[D[V]: dict[str, V]]: ...                  # not reducible: D is bounded by a partial application

type MyList[T] = list[T]                            # MyList eta-reduces to list
```

The bound and default are the only places an inner parameter may be referenced outside of its declaration.

## Specification
### Type Constructor Parameter Declarations
### Arity and Inner Type Parameters
### Scoping and Shadowing
### Upper Bounds and Constraints
### Defaults and Eta-Reduction
### Variance
### Application Validation
### Call-Site Unification
### Behavior When Type Arguments Are Omitted
### Use in Type Aliases and Protocols
### Interaction with `ParamSpec` and `TypeVarTuple`
### Compatibility with Traditional `TypeVar`

## Runtime Implementation
### Grammar Changes
### AST Changes
### Evaluation Order and Scoping Behavior
### Library Changes

## Backwards Compatibility

## Security Implications

## How to Teach This

## Reference Implementation

## Rejected Ideas
### Anonymous Inner Parameter Spellings (`F[...]`, `F[_]`)
### Subscriptable `Self` (`Self[T]`)
### Dedicated Kinding Primitive (`KindVar`)
### Arbitrary Higher-Order Unification and Type-Level Lambdas

## Open Issues

## Appendix A: Survey of Higher-Kinded Type Syntax in Other Languages
### C++
### Scala
### Haskell
### Rust
### TypeScript
### Swift
### OCaml
### Java and Kotlin
### Summary: Why So Few Languages Support This, and Why Python Should

## Appendix B: Survey of Real-World Python Use Cases
### NumPy (`ndarray.view`)
### SciPy Sparse (`_spbase.astype`)
### SciPy Stats (`TransformedDistribution`)
### Django ORM (`Field.__new__`)
### Django Admin (`admin.register`)
### TensorFlow (`GradientTape.gradient`)
### Gevent (`gevent.pool.Group`)
### Python Standard Library (`dict.fromkeys` and `bidict.inverse`)

## Acknowledgements

## References

## Copyright
