"""
Higher-Kinded Type (HKT) Error Diagnostics & Misuse Catalog

This file documents intentional error diagnostics and guardrails implemented
in Pyright for Higher-Kinded Types (python/typing#548).

Each case demonstrates how Pyright guides developers when HKT syntax or type
constructors are misused.
"""

from typing import Any, Protocol
from collections.abc import Collection


# ==============================================================================
# Error Category 1: Non-generic class passed to Type Constructor parameter
# Diagnostic: "{type}" is not a generic type constructor
# Origin: python/typing#548 comment 843663432 (Tinche - Mongo ODM)
# ==============================================================================

class ObjectId:
    pass

class MongoModel[ID](Protocol):
    __collection__: str
    _id: ID

class SpecialMongoModel[ID]:
    __collection__: str = "special"
    def __init__(self, id: ID) -> None:
        self._id = id

class NonGenericUser:
    __collection__ = "users"
    _id: ObjectId

class ConcreteUser(MongoModel[ObjectId]):
    __collection__ = "users"
    _id: ObjectId

def find_one[IDT, MongoModelT[T]: MongoModel[T]](
    model_cls: type[MongoModelT[IDT]], id: IDT
) -> MongoModelT[IDT]:
    ...

# Valid HKT application: SpecialMongoModel is a generic constructor (kind * -> *)
# and is specialized to int:
find_one(SpecialMongoModel, 123)  # OK -> SpecialMongoModel[int]

# ERROR: NonGenericUser is a 0-ary (proper) class, not a generic constructor.
# It cannot be parameterized as NonGenericUser[ObjectId].
# Expected diagnostic:
#   Argument of type "type[NonGenericUser]" cannot be assigned to parameter "model_cls"
#   "type[NonGenericUser]" is not a generic type constructor
find_one(NonGenericUser, ObjectId())

# ERROR: ConcreteUser pre-binds ID=ObjectId, so it is a proper type (kind *),
# not a 1-ary type constructor.
# Expected diagnostic:
#   Argument of type "type[ConcreteUser]" cannot be assigned to parameter "model_cls"
#   "MongoModel[ObjectId]" is not a concrete class type and cannot be assigned to type ...
find_one(ConcreteUser, ObjectId())


# ==============================================================================
# Error Category 2: Type Parameter Count Mismatch (Arity Mismatch)
# Diagnostic: "{type}" has {received} type parameters, but type constructor "{name}" requires {expected}
# ==============================================================================

class BinaryMap[K, V]:
    pass

def expect_unary_constructor[T[X]](ctor: type[T[Any]]) -> None:
    ...

# ERROR: BinaryMap requires 2 type parameters, but T requires 1.
# Expected diagnostic:
#   "type[BinaryMap[K@BinaryMap, V@BinaryMap]]" has 2 type parameters, but type constructor "T" requires 1
expect_unary_constructor(BinaryMap)


# ==============================================================================
# Error Category 3: Upper Bound / Subtyping Violation on Type Constructor
# Diagnostic: Type constructor "{name}" has upper bound "{bound}"
# ==============================================================================

class UnrelatedContainer[T]:
    pass

def expect_collection_constructor[C[X]: Collection[X]](ctor: type[C[Any]]) -> None:
    ...

# Valid: list is a 1-ary constructor satisfying Collection[X]
expect_collection_constructor(list)  # OK

# ERROR: UnrelatedContainer does not derive from Collection.
# Expected diagnostic:
#   Argument of type "type[UnrelatedContainer[T@UnrelatedContainer]]" cannot be assigned...
#   Type "UnrelatedContainer[Any]" is not assignable to upper bound "Collection[X@C]"
expect_collection_constructor(UnrelatedContainer)

# ERROR: dict has 2 type parameters but C requires 1; cannot partially apply.
# Expected diagnostics:
#   "type[MutableMapping[_KT@dict, _VT@dict]]" has 2 type parameters, but type constructor "C" requires 1
#   Type constructor "C" has upper bound "Collection[X@C]"
#   Generic class "type[MutableMapping[_KT@dict, _VT@dict]]" cannot be partially applied to satisfy type constructor "C"
expect_collection_constructor(dict)


# ==============================================================================
# Error Category 4: Constraint Set Violation on Type Constructor
# Diagnostic: Type "{type}" is not assignable to constrained type variable "{name}"
# ==============================================================================

def expect_list_or_set[C[X]: (list[X], set[X])](ctor: type[C[Any]]) -> None:
    ...

# Valid: list and set are members of the constraint tuple
expect_list_or_set(list)  # OK
expect_list_or_set(set)   # OK

# ERROR: tuple is a 1-ary constructor but is not in (list, set).
# Expected diagnostic:
#   Argument of type "type[tuple[_T_co@tuple]]" cannot be assigned to parameter "ctor"
#   Type "tuple[Any]" is not assignable to constrained type variable "C@expect_list_or_set"
expect_list_or_set(tuple)


# ==============================================================================
# Error Category 5: Template Parameter Bound Violation
# Diagnostic: "{received}" is not assignable to "{expected_bound}"
# Origin: python/typing#548 comment 701207531 (Array / Scalar bound)
# ==============================================================================

class Scalar:
    pass

class IntScalar(Scalar):
    pass

class NotScalar:
    pass

class Array[T]:
    pass

class ChunkedArray[T]:
    pass

def preserve_array[S: Scalar, F: (Array[S], ChunkedArray[S])](value: F[S]) -> F[S]:
    ...

# Valid: IntScalar satisfies upper bound Scalar
preserve_array(Array[IntScalar]())  # OK

# ERROR: NotScalar violates the template parameter bound S: Scalar.
# Expected diagnostic:
#   Argument of type "Array[NotScalar]" cannot be assigned to parameter "value"
#   "NotScalar" is not assignable to "Scalar"
preserve_array(Array[NotScalar]())


# ==============================================================================
# Error Category 6: Type Variable Scope Shadowing in Constructor Parameters
# Diagnostic: TypeVar "{name}" is already in use by an outer scope
# ==============================================================================

# ERROR: Inner dummy parameter IDT shadows the outer function type parameter IDT.
# Expected diagnostic:
#   TypeVar "IDT" is already in use by an outer scope
def find_one_shadowed[IDT, MongoModelT[IDT]: MongoModel[IDT]](
    model_cls: type[MongoModelT[IDT]], id: IDT
) -> MongoModelT[IDT]:
    ...


# ==============================================================================
# Error Category 7: Definition-Site: Applying Unconstrained TypeVar to Constrained Constructor
# Diagnostic: Type "{type}" cannot be assigned to type variable "{name}"
# ==============================================================================

class IntBox[X: int]:
    pass

class StrOrIntBox[X: (int, str)]:
    pass

# ERROR: In the function definition, constructor F requires X to be bounded by int (F[X: int]).
# Applying unconstrained T (whose upper bound is object) violates the constructor's bound at definition time.
# Expected diagnostic:
#   Type "T@bad_bound_apply" cannot be assigned to type variable "X@F"
#   Type "object*" is not assignable to upper bound "int" for type variable "X@F"
#   "object*" is not assignable to "int" (reportInvalidTypeArguments)
def bad_bound_apply[T, F[X: int]: IntBox[X]](x: F[T]) -> None:
    ...

# ERROR: In the function definition, constructor C requires X to be constrained to (int, str).
# Applying unconstrained U violates the constructor's constraint set at definition time.
# Expected diagnostic:
#   Type "U@bad_constraint_apply" cannot be assigned to type variable "X@C"
#   Type "U@bad_constraint_apply" is not assignable to constrained type variable "X@C" (reportInvalidTypeArguments)
def bad_constraint_apply[U, C[X: (int, str)]: StrOrIntBox[X]](x: C[U]) -> None:
    ...

# ERROR: Template-parameter bound mismatch at definition site:
# Constructor F is constrained to (Array[S], ChunkedArray[S]) where S has upper bound Scalar.
# Applying unconstrained T violates the template parameter bound S at definition time.
# Expected diagnostic:
#   Type "T@bad_template_bound_apply" cannot be assigned to type variable "S@bad_template_bound_apply"
#   Type "object*" is not assignable to upper bound "Scalar" for type variable "S@bad_template_bound_apply"
#   "object*" is not assignable to "Scalar" (reportInvalidTypeArguments)
def bad_template_bound_apply[S: Scalar, T, F: (Array[S], ChunkedArray[S])](x: F[T]) -> None:
    ...


# ==============================================================================
# Error Category 8: Applying Arguments to Non-Constructor TypeVars
# Diagnostic: TypeVar "{name}" is not subscriptable
# ==============================================================================

# ERROR: T is declared as a standard type parameter (kind *), not a type constructor T[X].
# Subscripting it with [int] is illegal.
# Expected diagnostic:
#   TypeVar "type[T@bad_applied_typevar]" is not subscriptable
def bad_applied_typevar[T](x: T[int]) -> None:
    ...


# ==============================================================================
# Error Category 9: Inconsistent Constructor Solving Across Arguments
# Diagnostic: Argument of type "{type2}" cannot be assigned to parameter "{param}" of type "{type1}"
# Origin: higherKindedType2.py
# ==============================================================================

class BoxA[T]:
    pass

class BoxB[T]:
    pass

def same_constructor[T, F: (BoxA[T], BoxB[T])](first: F[int], second: F[str]) -> None:
    ...

# ERROR: `first` solves F to BoxA, but `second` provides BoxB[str].
# Expected diagnostic:
#   Argument of type "BoxB[str]" cannot be assigned to parameter "second" of type "BoxA[str]"
same_constructor(BoxA[int](), BoxB[str]())


# ==============================================================================
# Error Category 10: Mixed-Kind Usage Within the Same Scope
# Diagnostic: Expected type arguments for generic class "{name}"
# Origin: higherKindedType9Pep695.py
# ==============================================================================

# ERROR: Mixed cannot be used as both an unapplied 0-ary type and an applied type constructor in the same scope.
# Expected diagnostic:
#   Expected type arguments for generic class "Mixed" (reportGeneralTypeIssues)
def rejects_mixed_kind[T, Mixed: (BoxA[T], BoxB[T])](value: Mixed, item: Mixed[int]) -> None:
    ...


# ==============================================================================
# Error Category 11: Inconsistent Arity in Constructor Constraint Tuples
# Diagnostic: TypeVar "{name}" is not subscriptable
# Origin: higherKindedType13.py
# ==============================================================================

class BinaryConstructor[K, V]:
    pass

# ERROR: Constructor constraints mix 1-ary BoxA[T] with 2-ary BinaryConstructor[K, V].
# Expected diagnostic:
#   TypeVar "type[F@bad_arity_constraints]" is not subscriptable (reportGeneralTypeIssues)
def bad_arity_constraints[T, K, V, F: (BoxA[T], BinaryConstructor[K, V])](value: F[int]) -> None:
    ...


# ==============================================================================
# Error Category 12: Mixing Generic Constructors and Concrete Classes in Constraints
# Diagnostic: TypeVar "{name}" is not subscriptable
# Origin: higherKindedType13.py
# ==============================================================================

class NonGenericConcrete:
    pass

# ERROR: Constructor constraint tuple mixes generic BoxA[T] with non-generic class NonGenericConcrete.
# Expected diagnostic:
#   TypeVar "type[F@bad_generic_mix]" is not subscriptable (reportGeneralTypeIssues)
def bad_generic_mix[T, F: (BoxA[T], NonGenericConcrete)](value: F[int]) -> None:
    ...


# ==============================================================================
# Error Category 13: Rejecting TypeVarTuple and ParamSpec as Constructors
# Diagnostic: TypeVarTuple / ParamSpec is not allowed in this context
# Origin: higherKindedType13.py
# ==============================================================================

# ERROR: TypeVarTuple (*Ts) cannot be subscripted as a type constructor.
# Expected diagnostic:
#   TypeVarTuple is not allowed in this context (reportInvalidTypeForm)
def rejects_type_var_tuple[*Ts](value: Ts[int]) -> None:
    ...

# ERROR: ParamSpec (**P) cannot be subscripted as a type constructor.
# Expected diagnostic:
#   ParamSpec is not allowed in this context (reportInvalidTypeForm)
def rejects_param_spec[**P](value: P[int]) -> None:
    ...


# ==============================================================================
# Error Category 14: Variance Violations in Constructor Application
# Diagnostic: "{source}" is not assignable to "{dest}"
# Origin: higherKindedType12.py
# ==============================================================================

class Animal:
    pass

class Dog(Animal):
    pass

class InvariantContainer[T]:
    def __init__(self, val: T) -> None:
        self.val = val

def accepts_invariant_container[T, F: InvariantContainer[T]](value: F[Animal]) -> None:
    ...

# ERROR: InvariantContainer is invariant in T (mutable attribute `val`).
# Dog is a subtype of Animal, but invariant container invariance requires exact type match.
# Expected diagnostic:
#   Argument of type "InvariantContainer[Dog]" cannot be assigned to parameter "value" of type "F@accepts_invariant_container[Animal]"
#   "InvariantContainer[Dog]" is not assignable to "InvariantContainer[Animal]"
#   Type parameter "T@InvariantContainer" is invariant, but "Dog" is not the same as "Animal" (reportArgumentType)
dog_container: InvariantContainer[Dog] = InvariantContainer(Dog())
accepts_invariant_container(dog_container)


# ==============================================================================
# Error Category 15: Concrete Type Bounds & Constraints Rejecting Subscripting
# Diagnostic: TypeVar "{name}" is not subscriptable
# Origin: higherKindedType9Pep695.py
# ==============================================================================

# ERROR: Bound is bounded by non-generic type `int`. It is not a type constructor.
# Expected diagnostic:
#   TypeVar "type[Bound@rejects_concrete_bound]" is not subscriptable (reportGeneralTypeIssues)
def rejects_concrete_bound[Bound: int](value: Bound[int]) -> None:
    ...

# ERROR: Constrained is constrained to non-generic types (int, str). It is not a type constructor.
# Expected diagnostic:
#   TypeVar "type[Constrained@rejects_concrete_constraint]" is not subscriptable (reportGeneralTypeIssues)
def rejects_concrete_constraint[Constrained: (int, str)](value: Constrained[int]) -> None:
    ...
