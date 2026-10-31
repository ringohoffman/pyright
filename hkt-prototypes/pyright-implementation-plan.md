# Pyright HKT Reference Implementation: Cleanup, Hardening & Verification Plan

Branch: `higher-kinded-types` (merge-base `916d7dc62` with `upstream/main`)
Companion: [pep-draft-outline.md](pep-draft-outline.md)

This plan takes the current prototype — which proves the semantics in the PEP are implementable — and turns it into a
reference implementation that a pyright maintainer could review. It is organized into phases that are each
independently verifiable. Phases 1–3 are blockers; 4–6 are what make it reviewable; 7 is release prep.

---

## 0. Ground rules

These apply to every phase.

| Rule | Rationale |
| --- | --- |
| **No mutation of `TypeVarDetailsShared` after declaration.** Constructor-ness, `typeParams`, and `typeVarScopeId` are set exactly once in `getTypeOfTypeParam` / `createTypeVarType`. | Evaluator results must be idempotent and order-independent. The current eval-time mutation is the root cause of 9 of 11 regressions. |
| **Every downstream site asks `TypeVarType.isConstructor(tv)` and reads `tv.shared.typeParams`.** Never `getTypeVarArgsRecursive(tv.shared.boundType)` to discover arity. | One source of truth. Eliminates the two parallel encodings of "constructor". |
| **Gate everything behind `enableExperimentalFeatures`** until the PEP is accepted. Parser emits an error for the `F[T]` syntax when the flag is off (or `pythonVersion < 3.16`). | Pyright policy: unaccepted PEPs ship only as experimental. This is how TypedDict `closed=` and `TypeForm` landed. |
| **Zero regressions in `upstream/main` tests.** Any change to an existing sample's expected count requires a written justification per `.github/agents/pyright-test-policy.md`. | Tests are the spec. |
| **New behavior is tested via `.py` samples**, not hand-built `ClassType` fixtures in `types.test.ts`. | Project convention; fixtures are brittle and unreadable to reviewers. |
| **Each phase ends with the full evaluator/checker suite green**: `pnpm exec jest typeEvaluator checker types --forceExit`. | Catches cross-phase breakage early. |

---

## 1. Fix the 11 upstream regressions

### 1.1 Current failures and root causes

| Test | File | Symptom | Root cause |
| --- | --- | --- | --- |
| `Self1`, `Self2`, `Self5`, `Self6` | typeEvaluator8 | `type[Self]` → `Unknown`; "Expected no type arguments for class Self"; spurious "Self cannot be used in a function with a cls parameter…" | **A** |
| `Super1` | typeEvaluator2 | `"Self" cannot be instantiated` (31:16) | **A** |
| `Solver19` | typeEvaluator2 | `type[Self]` not assignable to `type[_T1]` (25:46) | **A** |
| `Protocol29` | typeEvaluator7 | `partial[int]` not assignable to `Partial[int]`; spurious Self error | **A** (verify after fix; may also touch the `assignType` HKT branch) |
| `TypeNarrowingIsinstance2` | typeEvaluator1 | `Self@ClassE` narrows to `<subclass of int and Self>` | **A** |
| `None1` | typeEvaluator6 | `type[Self]` not assignable to `type[None]` (23:7) | **A** |
| `Annotations1` | typeEvaluator1 | Expected 21 errors, got 20 (one diagnostic suppressed) | **B** — bisect |
| `TypeParams3` | typeEvaluator5 | Expected 8 errors, got 7 (one `"X" is not defined` suppressed) | **B** — bisect; likely binder/scope change |

**Root cause A — eval-time reclassification.** Three sites inspect a TypeVar's bound, find type args that are
TypeVars, and mutate `shared.typeParams`:

- [typeEvaluator.ts L5905–L5935](../packages/pyright-internal/src/analyzer/typeEvaluator.ts#L5905-L5935) — bare-name path in `validateSymbolIsAccessible`/name evaluation
- [typeEvaluator.ts L8222–L8260](../packages/pyright-internal/src/analyzer/typeEvaluator.ts#L8222-L8260) — subscript-on-TypeVar path in `getTypeOfIndexWithBaseType`
- [typeEvaluator.ts L8282–L8285](../packages/pyright-internal/src/analyzer/typeEvaluator.ts#L8282-L8285) — synthesized `T0, T1, …` fallback

`Self` is synthesized with bound `ClassName[_P@ClassName, …]`, so `getTypeVarArgsRecursive(bound)` is non-empty and
`Self` becomes a "constructor".

**Root cause B — suppressed diagnostics.** Two candidates: (i) the `AllowMissingTypeArgs` flag leaking into
non-HKT paths via `getTypeArgs` ([L9008–L9016](../packages/pyright-internal/src/analyzer/typeEvaluator.ts#L9008-L9016))
when `options.isTypeClass` is set; (ii) the binder/`getExecutionScopeNode` changes in
[parseTreeUtils.ts L1101–L1124](../packages/pyright-internal/src/analyzer/parseTreeUtils.ts#L1101-L1124).

### 1.2 Tasks

1. **Move implicit-constructor detection to declaration time.**
   - In `getTypeOfTypeParam` (PEP 695) after the bound/constraints are evaluated: if `node.d.typeParams` is absent and
     the bound (or every constraint) is a class instance whose `typeArgs` contain TypeVars from an *enclosing live
     scope*, set `shared.typeParams` to those TypeVars. Never do this for `isSynthesized` or `isSelf` TypeVars.
   - In `createTypeVarType` (legacy `TypeVar(...)`) do the same for `bound=`/constraints, limited to module-scope
     TypeVars as `isAllowedTypeVarTemplateConstraint` already encodes.
   - Delete the three eval-time mutation blocks. Replace them with `if (!TypeVarType.isConstructor(tv)) { report typeVarNotSubscriptable; return Unknown }`.
2. **Guard every constructor-specific branch with `!tv.shared.isSynthesized`** as a belt-and-braces check
   (`assignTypeVar`, `applyTypeArgToTypeVar`, `makeTopLevelTypeVarsConcrete`, `ApplySolvedTypeVarsTransformer`).
3. **Bisect `Annotations1` and `TypeParams3`.** Revert the `AllowMissingTypeArgs`/`isTypeClass` plumbing and the
   `getExecutionScopeNode` change in isolation to find which suppresses the diagnostic; fix the leak so the flag only
   applies when the *formal* type param at that index is a constructor.
4. Re-run the HKT suite; expect no change in the 35 HKT sample counts. If a sample count changes, the sample was
   relying on the implicit path — update the sample to use the explicit `F[T]` spelling or the `D: dict[T, S]` spelling
   and document why.

### 1.3 Verification

```bash
cd packages/pyright-internal
pnpm exec jest typeEvaluator8.test -t "Self1|Self2|Self5|Self6" --forceExit
pnpm exec jest typeEvaluator2.test -t "Super1|Solver19" --forceExit
pnpm exec jest typeEvaluator1.test -t "TypeNarrowingIsinstance2|Annotations1" --forceExit
pnpm exec jest typeEvaluator5.test typeEvaluator6.test typeEvaluator7.test -t "TypeParams3|None1|Protocol29" --forceExit
pnpm exec jest typeEvaluator7.test -t "HigherKindedType" --forceExit
```

Exit criterion: all 11 pass, all 35 HKT samples pass with unchanged counts.

---

## 2. Delete dead code

### 2.1 Inventory

Never set, never reached:

| Symbol | Location |
| --- | --- |
| `TypeVarDetailsShared.requiresTupleMapTranspose` | types.ts L2857, L3215 |
| `TypeVarTupleDetailsPriv.mappedConstructor` | types.ts L2961 |
| `TypeVarType.cloneForMappedTypeVarTuple` | types.ts L3033–L3037 |
| `specializeMappedConstructor`, `getMappedConstructorTypeArg`, `stripMappedPackLiteral` | typeUtils.ts L2902–L2963 |
| Transpose + mapped-extraction blocks in `assignTypeVar` | constraintSolver.ts L122–L178 |
| Mapped-tuple branch in `ApplySolvedTypeVarsTransformer.transformTypeVar` | typeUtils.ts L4549–L4600 |

Also inspect for removal after Phase 1 makes them unreachable:

- `isAllowedTypeVarTemplateConstraint`'s `isPep695 === false` branch if legacy `TypeVar(bound=Array[T])` support is
  dropped from the PEP (see §6.2).
- `GetTypeArgsOptions.isTypeClass` if bisect in §1.2 shows it's the leak and `type[D[T, S]]` can be handled by
  the `typeParams` path instead.

### 2.2 Verification

```bash
pnpm run check:eslint          # unused-import / unused-var errors will surface leftovers
pnpm exec jest types.test typeEvaluator7.test --forceExit
```

Exit criterion: `grep -rn "mappedConstructor\|requiresTupleMapTranspose" packages/pyright-internal/src` returns nothing.

---

## 3. Version / feature gating

### 3.1 Tasks

1. **Parser.** In `_parseTypeParameter` ([parser.ts L686–L689](../packages/pyright-internal/src/parser/parser.ts#L686-L689)),
   after parsing the inner list, emit `LocMessage.typeParamConstructorSyntaxIllegal()` when
   `!isStubFile && pythonVersion < 3.16`. Mirror the existing PEP 695 gate at L598 and L2178.
2. **Evaluator.** Any site that *creates* a constructor TypeVar (explicit `F[T]`, implicit `D: dict[T, S]`, legacy
   `TypeVar(bound=...)`) checks `fileInfo.diagnosticRuleSet.enableExperimentalFeatures`; when off, report
   `LocMessage.typeVarConstructorExperimental()` once at the declaration and treat the TypeVar as an ordinary TypeVar
   (so downstream code never sees `isConstructor() === true`).
3. **Test config.** `typeEvaluator7.test.ts` HKT block already uses a `configOptions`; confirm it sets
   `pythonVersion = 3.16` and `enableExperimentalFeatures = true`. Add one negative sample
   (`higherKindedTypeGate1.py`) run *without* the flag that expects exactly the gate diagnostics.

### 3.2 Verification

- New sample test with flag off: N gate errors, zero other errors.
- Full suite still green (no other sample uses the syntax).

---

## 4. Restructure the type evaluator changes

Goal: a reviewer can read each HKT behavior as one named function with a docstring that cites the PEP section.

### 4.1 Extract `assignTypeToAppliedTypeVar`

The 400-line block at [typeEvaluator.ts L26374–L26772](../packages/pyright-internal/src/analyzer/typeEvaluator.ts#L26374-L26772)
becomes:

```
function assignTypeToAppliedTypeVar(destType: TypeVarType /* has priv.typeArgs */, srcType, diag, constraints, flags, recursionCount): boolean
  ├─ normalizeAppliedSource(destType, srcType): { effectiveSrc: ClassType; constructor: ClassType } | undefined
  │     handles: Any/Unknown/Never/union early-outs; unspecialized alias; unspecialized class;
  │              subclass-of-bound (MRO walk → specializeForBaseClass)
  ├─ matchConstructorAgainstBound(destType, constructor, …): ClassType | undefined   // PEP §Upper Bounds
  ├─ matchConstructorAgainstConstraints(destType, constructor, …): ClassType | undefined
  ├─ unifyAppliedTypeArgs(destType, template, effectiveSrc, …): boolean            // PEP §Call-Site Unification
  │     variance-aware per-arg assignType; template specialization via ConstraintSolution
  └─ recordConstructorSolution(constraints, destType, constructor): boolean
        existing-solution identity check + setBounds
```

Each helper ≤ 60 lines. The `originalSrcClass`/`effectiveSrcClass`/`constructorType`/`constructorTypeForConstraint`
quartet collapses into the `normalizeAppliedSource` return value.

### 4.2 Factor the arity-mismatch diagnostic

The `typeVarConstructorTypeParamCountMismatch` + `BoundContext` / `ConstraintContext` + `CannotPartiallyApply`
addendum block is copy-pasted in `assignTypeVar` (constraintSolver L183–L240), `assignTypeToAppliedTypeVar`,
and `applyTypeArgToTypeVar` (L30246–L30304). Replace with one
`addConstructorArityMismatchAddendum(diag, destType, srcType, expected, received)` in `typeEvaluator.ts`
(exposed via `TypeEvaluator` interface for `constraintSolver.ts`).

### 4.3 Remove `as any`

[decorators.ts L498–L502](../packages/pyright-internal/src/analyzer/decorators.ts#L498-L502) and
[typeEvaluator.ts L2535–L2540](../packages/pyright-internal/src/analyzer/typeEvaluator.ts#L2535-L2540): replace with a
single helper in `typeUtils.ts`:

```ts
export function isAppliedConstructorTypeVar(type: Type): type is TypeVarType {
    return isTypeVar(type) && type.priv.typeArgs !== undefined;
}
export function hasAppliedConstructorClsParam(fn: FunctionType): boolean
```

### 4.4 Fix the `getTypeOfBoundMember` hot path

[L2528–L2549](../packages/pyright-internal/src/analyzer/typeEvaluator.ts#L2528-L2549) does `lookUpClassMember` +
`getDeclaredTypeOfSymbol` on *every* member access. Options, in order of preference:

1. Skip `specializeWithDefaultTypeArgs` only when `objectType.shared.typeParams.length > 0 && !objectType.priv.typeArgs`
   *and* the eventual bound method's first param is an applied constructor TypeVar — i.e. move the check to after
   member lookup, where the function type is already in hand, and re-specialize only if needed.
2. If (1) is not possible, cache a per-class `ClassTypeFlags.HasConstructorClsMethod` bit computed once in
   `getTypeOfClass` by scanning declared classmethods/`__new__`.

Benchmark before/after with `build/perfCompare.py` on a large project (e.g. the pyright bundled typeshed checker run) —
required because this path is the hottest in the evaluator.

### 4.5 Consolidate template-specialization helpers

`makeTopLevelTypeVarsConcrete` ([L4616–L4670](../packages/pyright-internal/src/analyzer/typeEvaluator.ts#L4616-L4670)),
`ApplySolvedTypeVarsTransformer.transformTypeVar` (typeUtils L4606–L4700), and `assignTypeToAppliedTypeVar` all build a
`ConstraintSolution` mapping `shared.typeParams[i] → priv.typeArgs[i]` and call `applySolvedTypeVars`. Extract
`specializeConstructorTemplate(template: Type, typeVar: TypeVarType, appliedArgs: Type[]): Type` into `typeUtils.ts`.

### 4.6 Checker: make the return-only rule a real rule

[checker.ts L2527–L2539](../packages/pyright-internal/src/analyzer/checker.ts#L2527-L2539) overloads the single-use
TypeVar check. Split into:

- Constructor TypeVars are exempt from the single-use check (they are intrinsically multi-use via application).
- New diagnostic `typeVarConstructorReturnOnly` under `reportGeneralTypeIssues` when a constructor TypeVar appears in
  the return type and in no parameter. Own localized message, own sample.

### 4.7 Inner type param scope type

[L24259](../packages/pyright-internal/src/analyzer/typeEvaluator.ts#L24259) assigns `TypeVarScopeType.Function` to
inner params. Add `TypeVarScopeType.TypeParameter` and ensure `getTypeVarScopesForNode` / `validateTypeVarDefault` treat
it as live only within the owning `TypeParameterNode`'s bound/default (PEP §Scoping and Shadowing).

### 4.8 Verification

- Full suite green after each extraction (4.1 → 4.7 sequential; each is its own commit).
- `pnpm run check` clean.
- Perf: `perfCompare.py` delta for 4.4 within noise (< 2%).
- Diff size target: analyzer changes ≤ 1,200 lines (from ~1,600) with no loss of behavior.

---

## 5. Test suite restructuring

### 5.1 Shrink `types.test.ts`

Currently +3,365 lines of hand-built fixtures. For each `test(...)`:

| If it tests… | Then… |
| --- | --- |
| end-to-end inference (e.g. "ApplySolvedTypeVarsPreservesHigherKindedConstructorFamily") | Convert to a `.py` sample with `reveal_type(..., expected_text=...)`; delete the fixture. |
| a `typeUtils` function in isolation with no evaluator (e.g. `validateTypeVarDefault` edge) | Keep, but ≤ 40 lines each; share fixtures via a small `createClass(name, typeParams)` helper at the top of the file. |
| something already covered by an existing `higherKindedTypeN.py` | Delete. |

Target: `types.test.ts` ≤ 400 lines total.

### 5.2 Normalize sample files

Current set: `higherKindedType1–31.py` plus four `*Pep695.py` variants. Reorganize so a reviewer can map samples to
PEP sections:

| Sample | PEP section | Spelling |
| --- | --- | --- |
| `hktDeclaration1.py` | Type Constructor Parameter Declarations | `F[T]` on function, class, alias |
| `hktDeclaration2.py` | same | implicit `D: dict[T, S]` |
| `hktArity1.py` | Arity and Inner Type Parameters | too-many/too-few; partial application rejected |
| `hktScoping1.py` | Scoping and Shadowing | inner param invisible to body; shadowing an outer T |
| `hktBound1.py` | Upper Bounds and Constraints | bound, union bound, constraints, protocol bound |
| `hktBound2.py` | same | inner param bound (`F[X: int]`) violated at application |
| `hktDefault1.py` | Defaults and Eta-Reduction | `= Greenlet[T]` vs `= Greenlet` |
| `hktVariance1.py` | Variance | inferred variance through `F[...]` |
| `hktApplication1.py` | Application Validation | `Batch[list]` ok, `Batch[int]` error |
| `hktUnification1.py` | Call-Site Unification | `fromkeys`, `inverse`, `swap`; subclass-of-bound |
| `hktUnification2.py` | same | conflicting solutions for the same constructor across args |
| `hktOmittedArgs1.py` | Behavior When Type Arguments Are Omitted | bare `F` in annotation |
| `hktAlias1.py` | Use in Type Aliases and Protocols | |
| `hktParamSpec1.py` | Interaction with ParamSpec / TypeVarTuple | rejections |
| `hktLegacy1.py` | Compatibility with Traditional TypeVar | `TypeVar(bound=Array[T])` |
| `hktGate1.py` | (Phase 3) | flag off / old version |

Keep one `test()` per sample in `typeEvaluator7.test.ts` (or move the block to a new `hkt.test.ts` if the file is
getting long — check `jest` sharding config first). Every error in a sample must have a `# This should generate an
error` comment naming the expected message.

### 5.3 Fourslash coverage

Add at least:

- `hover.hkt.fourslash.ts` — hover over `D` in `cls: type[D[T, S]]` shows `D[T, S]` and over the call shows the solved
  class.
- `completions.hkt.fourslash.ts` — completions inside `F[` offer type names.
- `rename.hkt.fourslash.ts` — renaming the inner `T` in `F[T]` renames only within the bound/default.

### 5.4 Verification

```bash
pnpm exec jest typeEvaluator7.test -t "Hkt" --forceExit
pnpm exec jest fourslash -t "hkt" --forceExit
pnpm run test:norebuild            # full run before PR
```

---

## 6. Design decisions to lock down (PEP ↔ implementation)

Decide these before Phase 4 so the extraction targets the final semantics.

### 6.1 Is the implicit spelling (`D: dict[T, S]`) a separate declaration form or sugar?

- **Sugar (recommended):** declaration-time normalization sets `shared.typeParams = [T, S]`; everything else is the
  `F[T]` path. Simpler implementation, one code path. The PEP should say "equivalent to `D[T, S]: dict[T, S]`" explicitly.
- **Separate form:** keep two paths. Only justified if the PEP wants different unification rules (it currently doesn't).

### 6.2 Legacy `TypeVar(bound=Array[T])` support

`isAllowedTypeVarTemplateConstraint`'s legacy branch and the module-scope restriction exist only for this. The PEP's
"Compatibility with Traditional TypeVar" section is empty. Either specify it fully (and keep the code) or drop it
(delete ~80 lines). Recommendation: **drop for v1**; PEP 695 syntax is the primary target and `typing_extensions`
backport is a separate question.

### 6.3 Unsolved constructor TypeVar behavior

When `F` cannot be solved, what does `F[int]` become? Current code yields `Unknown`. Alternatives: the bound applied
(`Iterable[int]`), or an error. The PEP's "Behavior When Type Arguments Are Omitted" and "Call-Site Unification" sections
need to say. The implementation should then enforce it in `ApplySolvedTypeVarsTransformer` with `replaceUnsolved`.

### 6.4 Conflicting constructors across arguments

`def f[F[T]](a: F[int], b: F[str])` called with `f([1], {"x"})`. Current: `recordConstructorSolution` returns `false`
when `!isTypeSame(existing, new)`. Should it widen to a common base (`Collection`)? Pyright widens ordinary TypeVars
under some conditions. PEP should specify; recommendation is **no widening** (constructors are nominal).

### 6.5 Protocol bounds

`[F[T]: Iterable[T]]` with `F = MyCustomContainer` requires structural matching of the *constructor*, not an
instance. Current code specializes the candidate with the applied args and `assignType`s against the protocol — that's
right, but it's buried in the bound-matching loop. Make it a named case in `matchConstructorAgainstBound`.

---

## 7. PR preparation

### 7.1 Split

Upstream will not review a 7,000-line PR. Proposed stack, each independently green:

1. **Parser + AST + binder + stub renderer** for `F[T]` syntax, version-gated, no evaluation. Includes
   `parser.test.ts` and `binder.test.ts` samples. (~150 lines)
2. **Type model**: `TypeVarDetailsShared.typeParams/typeVarScopeId`, `TypeVarDetailsPriv.typeArgs`,
   `TypeVarType.isConstructor/cloneForTypeApplication`, `isTypeSame`, type printer. (~150 lines)
3. **Declaration-time evaluation**: `getTypeOfTypeParam` inner params, bound/default/eta-reduction validation,
   `verifyConstructorInnerParamsUsed`, scoping. Samples: `hktDeclaration*`, `hktArity*`, `hktScoping*`,
   `hktBound*`, `hktDefault*`. (~400 lines)
4. **Application + unification**: subscript on constructor TypeVar, `assignTypeToAppliedTypeVar`,
   `assignTypeVar`/`applyTypeArgToTypeVar` arity checks, `ApplySolvedTypeVarsTransformer`,
   `makeTopLevelTypeVarsConcrete`. Samples: `hktApplication*`, `hktUnification*`, `hktAlias*`. (~600 lines)
5. **Checker + classmethod/`__new__` integration**: `getTypeOfBoundMember`, decorators, single-use rule.
   Samples: `hktUnification1.py` `fromkeys` cases, fourslash. (~150 lines)

### 7.2 Per-PR checklist

- [ ] `pnpm run check` clean
- [ ] `pnpm run test:norebuild` green
- [ ] `build/perfCompare.py` delta reported in PR description (required for PR 4 and 5)
- [ ] Every new localized message has an entry in `package.nls.en-us.json` and is exercised by a sample
- [ ] No `as any`, no `!` non-null assertions on new code paths without a comment
- [ ] `docs/type-concepts-advanced.md` gains an "Experimental: type constructor parameters" subsection (PR 4)
- [ ] PEP draft links to the PR stack under "Reference Implementation"

### 7.3 Conformance

The typing conformance suite (`python/typing` `conformance/tests`) will eventually need `generics_hkt_*.py` files.
Draft them alongside `hktUnification1.py` so the PEP's examples and pyright's samples are literally the same code.

---

## Appendix: Current-state metrics (baseline for measuring progress)

| Metric | Now | Target |
| --- | --- | --- |
| Analyzer diff lines | 1,640 | ≤ 1,200 |
| `types.test.ts` lines | 3,405 | ≤ 400 |
| Upstream test regressions | 11 | 0 |
| Dead code paths | 6 symbols / ~150 lines | 0 |
| `as any` casts | 2 | 0 |
| HKT sample files | 35 (numbered) | ~16 (named by PEP section) |
| Fourslash tests | 0 | ≥ 3 |
| Version/feature gate | none | parser + evaluator |
| Longest new function | ~400 lines (`assignType` branch) | ≤ 80 |
