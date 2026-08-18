# Higher-Kinded Types and Map Roadmap

This document is the handoff for the higher-kinded TypeVar and type-pack `Map` prototypes on the `higher-kinded-types` branch. It records the intended semantics, current implementation, executable specifications, known failures, and the order in which remaining work should proceed.

## Scope and decisions

The first HKT feature should extend `TypeVar`; it should not introduce `TypeConstructorVar`.

The current intended distinctions are:

- `T` used as an ordinary annotation is a TypeVar of kind `Type`.
- An unconstrained `F` first used as `F[A]` is inferred to be a unary constructor variable.
- A TypeVar cannot be both an ordinary type and a constructor in the same scope.
- Constructor identity is invariant: solving `F` to `Array` must preserve `Array` in the result.
- Arguments applied to a selected constructor follow that constructor's declared variance.
- An ordinary applied bound such as `bound=Array[object]` does not make a TypeVar subscriptable.
- Legacy and PEP 695 syntax must have equivalent behavior.

Bare generic-origin constraints such as `TypeVar("F", Array, ChunkedArray)` currently work, but they are design scaffolding. Normal Pyright semantics require generic classes to be parameterized. Applied-template constraints are the preferred design under investigation:

- Legacy: `F = TypeVar("F", Array[Scalar[D]], ChunkedArray[Scalar[D]])`
- PEP 695: a constructor family whose alternatives are parameterized templates rather than ordinary applied bounds

The exact PEP 695 declaration syntax for template-local parameters remains a specification question. Do not remove the competing tests until this is settled.

`Map` is a proposed explicit type-level operation over type packs. It avoids contextually interpreting `PyTree[*Ts]` as distribution.

- Unary mapping: `Map[F, *Ts]` produces `(F[T1], F[T2], ...)`.
- Arbitrary transpose: `Map[tuple, *Rows]`, where each element of `Rows` is a tuple carrier, transposes rows into positional tuples.
- Arbitrary zip: `*Map[Iterable, *ElementTs]` describes any number of iterable inputs whose result element is `tuple[*ElementTs]`.

## Current implementation

### Applied constructor TypeVars

The prototype stores constructor-use information directly on TypeVars:

- `TypeVarDetailsShared.constructorArity`
- `TypeVarDetailsShared.isUsedAsOrdinaryType`
- `TypeVarDetailsPriv.typeArgs`
- `TypeVarType.cloneForTypeApplication`

The evaluator accepts `F[A]`, infers and checks arity, rejects concrete bounds or constraints, and diagnoses mixed ordinary/constructor use.

The assignment path decomposes `F[A] <- Array[B]`, constrains `F` to the generic origin, constrains `A` from `B`, enforces constructor constraints or bounds, and preserves the selected constructor.

Solved constructors are reapplied in `ApplySolvedTypeVarsTransformer`, and the printer renders applied TypeVars.

### Type Server Protocol

TSP `TypeVarType` carries optional `typeArgs`, and the server has an in-process serialization test. The protocol version was advanced to `0.4.2`.

Pylance 2026.3.1 does not consume this new field, so active-Pylance hovers remain lossy. Use the Pyright Extension Development Host for end-to-end hover verification. See `hkt-prototypes/README.md`.

### Map prototype

`Map` is declared provisionally in the bundled `typing_extensions.pyi` as a special form.

The current internal representation reuses a TypeVarTuple clone with `priv.mappedConstructor`.

Implemented:

- Recognition of the `Map` special form.
- Output-only unary mapping over an already-solved TypeVarTuple.
- Specialization of class constructors and generic alias constructors.
- Inverse extraction of class, generic alias, and specialized generic base arguments during TypeVarTuple constraint collection.
- Positional transpose over an arbitrary number of finite tuple rows, including equal-width validation.
- Arbitrary-arity iterable zip inference through mapped generic base classes.

This representation is intentionally provisional. It supports one mapped constructor and marks tuple transpose through shared TypeVarTuple state, but it does not yet model mapping modes or multiple source packs explicitly.

## Test inventory

All tests are registered in `packages/pyright-internal/src/tests/typeEvaluator7.test.ts` and use Python 3.12 configuration.

### Green HKT gates

- `HigherKindedType1`: applied TypeVar representation and printing, legacy and PEP 695.
- `HigherKindedType2`: shared constructor inference and mixed-constructor rejection.
- `HigherKindedType3`: constructor reapplication from `F[A]` to `F[B]`.
- `HigherKindedType4`: cast-like `type[B]` selection preserving two outer constructors.
- `HigherKindedType5`: constructor arity consistency.
- `HigherKindedType6`: nested Arrow-shaped `F[Scalar[A]] -> F[Scalar[B]]`.
- `HigherKindedType8` and `HigherKindedType8Pep695`: constrained generic origins.
- `HigherKindedType9` and `HigherKindedType9Pep695`: when TypeVars can accept type arguments.
- `HigherKindedType13`: invalid constructor shapes, concrete/generic mixing, ParamSpec, and TypeVarTuple rejection.
- `HigherKindedType14`: binary constructor variables and reapplication.

### Red HKT specifications

- `HigherKindedType10` and `HigherKindedType10Pep695`: applied-template constraints, including nested `Scalar[D]` substitution.
- `HigherKindedType11` and `HigherKindedType11Pep695`: propagation of template parameter bounds.
- `HigherKindedType12`: covariance, invariance, and contravariance from the selected constructor slot.
- `HigherKindedType15`: applied bounds remain ordinary TypeVars and must reject subscription.
- `HigherKindedType16`: canonical Arrow-shaped applied-template acceptance test, including wrapper bodies.

### Map gates

- `HigherKindedMap1`: green. Output-only unary mapping produces exact `tuple[list[int], list[str], list[bytes]]` results in both syntaxes.
- `HigherKindedMap2`: green. JAX-style PyTree arguments infer a pairwise leaf pack for callback parameters in legacy and PEP 695 syntax. Recursive aliases print using Pyright's established expanded form.
- `HigherKindedMap3`: green. `Map[tuple, *Rows]` transposes one, two, or arbitrarily many finite tuple rows and rejects unequal widths.
- `HigherKindedMap4`: green. Arbitrary numbers of `Iterable[T]` inputs infer `Iterator[tuple[*ElementTs]]` without finite overloads.

## Roadmap: HKT completion

### Phase H1: Applied-template constraint semantics

1. Preserve generic template constraints instead of rejecting them as generic TypeVar constraints.
2. Define template parameters separately from function inference variables.
3. Match a concrete source against each template and record both the selected origin and template substitution.
4. Reapply a selected template with new arguments, including nested templates such as `Array[Scalar[D]]`.
5. Make `HigherKindedType10` green first, then `HigherKindedType10Pep695`.

Do not proceed to H2 until both gates pass independently.

### Phase H2: Template parameter bounds

1. Carry bounds and constraints from template parameters into application sites.
2. Reject substitutions that violate a template parameter bound.
3. Ensure bounds are enforced during both call-site solving and generic function body checking.
4. Make `HigherKindedType11` green, then `HigherKindedType11Pep695`.

### Phase H3: Variance

1. Derive argument variance from the selected class constructor's corresponding type parameter.
2. Preserve invariant constructor identity separately from argument variance.
3. Validate covariance, invariance, and contravariance in both legacy and PEP 695 portions of `HigherKindedType12`.
4. Add multi-parameter mixed-variance tests before implementing mixed variance.

### Phase H4: Bound semantics cleanup

1. Remove the current behavior that treats an applied bound's generic origin as a constructor family.
2. Keep applied bounds as ordinary TypeVar bounds.
3. Make `HigherKindedType15` green.
4. Decide whether constructor bounds are in scope. If they are, specify a distinct syntax; do not overload ordinary applied-bound semantics.

### Phase H5: Canonical Arrow acceptance

1. Make `HigherKindedType16` green using applied templates.
2. Update `hkt-prototypes/pyarrow-cast/cast_preserves_container.py` to the selected declaration syntax.
3. Include legacy and PEP 695 signatures.
4. Compare HKT reveals with overload reveals for both `Array` and `ChunkedArray`.
5. Keep `RecordBatch`, `Table`, and `_Tabular` out until they motivate a distinct constructor shape.

### Phase H6: Internal representation hardening

The current `TypeVarType` clone with `priv.typeArgs` is expedient. Before proposing upstream quality:

1. Audit equality, caching, free/bound cloning, recursive aliases, and unification variables.
2. Ensure shared `constructorArity` and `isUsedAsOrdinaryType` mutations do not leak between speculative evaluations or caches.
3. Consider an explicit internal applied-constructor type if clone metadata causes special cases to spread.
4. Add type-printer, serialization, and cache invalidation tests.

## Roadmap: Map completion

### Phase M1: Stabilize unary Map

1. `HigherKindedMap1` is green; keep it green while changing internals.
2. Add negative tests for wrong arity, non-constructor first arguments, non-pack second arguments, and packed `Map` used without `*`.
3. Add printing tests for `Map[F, *Ts]` before and after solving.
4. Decide whether `Map` belongs in `typing`, `typing_extensions`, or an experimental Pyright-only namespace during prototyping.

### Phase M2: Finish generic alias inverse mapping

Completed for the current scope:

1. The unspecialized alias constructor is preserved for `Map`.
2. Alias type arguments are extracted from each specialized variadic argument.
3. Recursive PyTree inference is pairwise correlated with callback parameters.
4. Reveal text follows Pyright's existing recursive-alias expansion policy rather than introducing a Map-specific printer rule.

Remaining: add explicit callback mismatch tests.

### Phase M3: Arbitrary transpose

Define `Map[tuple, *Rows]` as a transpose operation when every element of `Rows` is a tuple carrier:

Completed for one, two, and three finite rows. Row widths are validated, columns are constructed positionally, literals are stripped consistently, and unequal widths are rejected. Empty-input semantics remain undecided.

### Phase M4: Arbitrary iterable zip

Completed for the current scope. Sources are projected through matching specialized generic bases, element types are extracted positionally, and one, two, and three iterable examples pass in legacy and PEP 695 forms. This is the general typing model for built-in `zip` that finite overload sets cannot express.

### Phase M5: General multi-pack Map semantics

The representation needs to distinguish:

- Unary elementwise mapping over one direct pack.
- Inverse mapping from variadic constructor instances.
- Positional transpose over a pack of tuple carriers.
- Potential future mapping of an N-ary constructor over N explicit pack carriers.

Replace `mappedConstructor?: Type` with structured mapped-pack metadata before adding more modes. Include constructor, source packs, carrier mode, arity, and variance behavior.

### Phase M6: Map diagnostics and protocol support

1. Add localized diagnostics for Map argument count, constructor arity, invalid pack positions, unequal transpose widths, and unsupported unbounded packs.
2. Add parser/evaluator tests for legal and illegal unpack positions.
3. Extend type printing and TSP serialization for mapped packs if they can appear in hovers or public signatures.
4. Add Extension Development Host hover verification.

## Validation commands

Run one gate while implementing:

```bash
cd packages/pyright-internal
npx jest typeEvaluator7.test -t '^HigherKindedMap2$' --forceExit --runInBand
```

Run completed base HKT gates:

```bash
npx jest typeEvaluator7.test -t '^HigherKindedType([1-9]|8Pep695|9Pep695)$' --forceExit --runInBand
```

Run all HKT and Map gates, including intentionally red specifications:

```bash
npx jest typeEvaluator7.test -t 'HigherKinded(Type|Map)' --forceExit --runInBand
```

Compile after each implementation slice:

```bash
npm run build
```

Regression sequence after all red gates turn green:

```bash
npx jest typeEvaluator7.test typePrinter.test --forceExit --runInBand
npx jest typeServer.inProc.test --forceExit --runInBand
npm test
cd ../..
npm run check
```

Then rebuild editor artifacts:

```bash
npm run build:extension:dev
npm --prefix packages/pyright-typeserver run webpack
```

## Immediate next step

Return to HKT Phase H1 and work only on `HigherKindedType10`. Applied-template constraints are the next blocking semantic requirement. Keep all four `HigherKindedMap` gates and the completed HKT gate set green while implementing it.
