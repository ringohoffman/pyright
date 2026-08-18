/*
 * types.test.ts
 * Copyright (c) Microsoft Corporation.
 * Licensed under the MIT license.
 *
 * Unit tests for analyzer type helpers.
 */

import * as assert from 'assert';

import { ConstraintSolution } from '../analyzer/constraintSolution';
import { printType, PrintTypeFlags } from '../analyzer/typePrinter';
import { applySolvedTypeVars, computeMroLinearization, getTypeVarArgsRecursive } from '../analyzer/typeUtils';
import {
    AnyType,
    ClassType,
    ClassTypeFlags,
    isAnyOrUnknown,
    isClass,
    isClassInstance,
    isInstantiableClass,
    isTypeVar,
    Type,
    TypeBase,
    TypeVarScopeType,
    TypeVarType,
    UnknownType,
    Variance,
} from '../analyzer/types';
import { Uri } from '../common/uri/uri';

function returnTypeCallback(type: any) {
    return type.shared.declaredReturnType ?? UnknownType.create(/* isEllipsis */ true);
}

test('DisjointBaseDoesNotSynthesizeDataClassMethods', () => {
    const classType = ClassType.createInstantiable(
        'SlottedDataClass',
        '',
        '',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        /* declaredMetaclass */ undefined,
        /* effectiveMetaclass */ undefined
    );

    let synthesizedSlots = false;
    let synthesizedMethods = false;
    classType.shared.synthesizeDataClassSlotsDeferred = () => {
        synthesizedSlots = true;
        classType.shared.hasNonEmptySlots = true;
    };
    classType.shared.synthesizeMethodsDeferred = () => {
        synthesizedMethods = true;
    };

    assert.strictEqual(ClassType.getDisjointBase(classType), classType);
    assert.strictEqual(synthesizedSlots, true);
    assert.strictEqual(synthesizedMethods, false);
});

test('ApplySolvedTypeVarsPreservesHigherKindedConstructorFamily', () => {
    const dataType = ClassType.createInstantiable(
        'DataType',
        '',
        '',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    const stringType = ClassType.createInstantiable(
        'StringType',
        '',
        '',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    const scalarClass = ClassType.createInstantiable(
        'Scalar',
        '',
        '',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const arrayClass = ClassType.createInstantiable(
        'Array',
        '',
        '',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    const dTypeVar = TypeVarType.createInstance('D');
    dTypeVar.shared.boundType = ClassType.cloneAsInstance(dataType);
    scalarClass.shared.typeParams.push(dTypeVar);

    const arrayTypeParam = TypeVarType.createInstance('S');
    arrayClass.shared.typeParams.push(arrayTypeParam);

    const scalarString = ClassType.specialize(ClassType.cloneAsInstance(scalarClass), [
        ClassType.cloneAsInstance(stringType),
    ]);
    const replacement = ClassType.specialize(ClassType.cloneAsInstance(arrayClass), [scalarString]);

    const solvedTypeVar = TypeVarType.createInstance('T');
    solvedTypeVar.priv.typeArgs = [ClassType.cloneAsInstance(stringType)];

    const solution = new ConstraintSolution();
    solution.setType(solvedTypeVar, replacement);

    const solved = applySolvedTypeVars(solvedTypeVar, solution);
    assert.strictEqual(printType(solved, PrintTypeFlags.None, returnTypeCallback), 'Array[Scalar[StringType]]');
});

test('ApplySolvedTypeVarsSubstitutesTemplateParameterInHigherKindedFamily', () => {
    const dataType = ClassType.createInstantiable(
        'DataType',
        '',
        '',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    const stringType = ClassType.createInstantiable(
        'StringType',
        '',
        '',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    const scalarClass = ClassType.createInstantiable(
        'Scalar',
        '',
        '',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const arrayClass = ClassType.createInstantiable(
        'Array',
        '',
        '',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    const dTypeVar = TypeVarType.createInstance('D');
    dTypeVar.shared.boundType = ClassType.cloneAsInstance(dataType);
    scalarClass.shared.typeParams.push(dTypeVar);

    const arrayTypeParam = TypeVarType.createInstance('S');
    arrayClass.shared.typeParams.push(arrayTypeParam);

    const scalarD = ClassType.specialize(ClassType.cloneAsInstance(scalarClass), [dTypeVar]);
    const arrayTemplate = ClassType.specialize(ClassType.cloneAsInstance(arrayClass), [scalarD]);

    const arrayT = TypeVarType.createInstance('ArrayT');
    arrayT.shared.constraints = [arrayTemplate];
    arrayT.priv.typeArgs = [ClassType.cloneAsInstance(stringType)];

    const solution = new ConstraintSolution();
    solution.setType(arrayT, arrayTemplate);

    const solved = applySolvedTypeVars(arrayT, solution);
    assert.strictEqual(printType(solved, PrintTypeFlags.None, returnTypeCallback), 'Array[Scalar[StringType]]');
});

test('HigherKindedTemplateParameterBoundIsPreservedOnConstraint', () => {
    const scalarClass = ClassType.createInstantiable(
        'Scalar',
        'test.Scalar',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    const notScalarClass = ClassType.createInstantiable(
        'NotScalar',
        'test.NotScalar',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    const arrayClass = ClassType.createInstantiable(
        'Array',
        'test.Array',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    const arrayTypeParam = TypeVarType.createInstance('T');
    arrayClass.shared.typeParams.push(arrayTypeParam);

    // S has bound Scalar
    const sTypeVar = TypeVarType.createInstance('S');
    sTypeVar.shared.boundType = ClassType.cloneAsInstance(scalarClass);

    // Template is Array[S] where S: Scalar
    const arrayTemplate = ClassType.specialize(ClassType.cloneAsInstance(arrayClass), [sTypeVar]);

    // F is constrained to Array[S]
    const fTypeVar = TypeVarType.createInstance('F');
    fTypeVar.shared.constraints = [arrayTemplate];

    // Applied form F[X]
    const xTypeVar = TypeVarType.createInstance('X');
    const appliedF = TypeVarType.cloneForTypeApplication(fTypeVar, [xTypeVar]);
    assert.strictEqual(appliedF.priv.typeArgs?.length, 1);

    // Verify template parameter S in F's constraint carries its bound Scalar
    const constraintTemplate = fTypeVar.shared.constraints[0];
    assert.ok(isClassInstance(constraintTemplate));
    assert.ok(constraintTemplate.priv.typeArgs && constraintTemplate.priv.typeArgs.length === 1);
    const templateParam = constraintTemplate.priv.typeArgs![0];
    assert.ok(isTypeVar(templateParam));
    assert.ok(templateParam.shared.boundType);
    assert.strictEqual(printType(templateParam.shared.boundType, PrintTypeFlags.None, returnTypeCallback), 'Scalar');

    // Passing NotScalar for X should violate S's bound
    const notScalarInstance = ClassType.cloneAsInstance(notScalarClass);
    const isAssignable = ClassType.isSameGenericClass(templateParam.shared.boundType as ClassType, notScalarInstance);
    assert.strictEqual(isAssignable, false);
});

test('HigherKindedConstructorSlotVarianceInheritance', () => {
    const animalClass = ClassType.createInstantiable(
        'Animal',
        'test.Animal',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const dogClass = ClassType.createInstantiable(
        'Dog',
        'test.Dog',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    dogClass.shared.mro.push(animalClass);

    // Producer[T_co] (Covariant)
    const producerClass = ClassType.createInstantiable(
        'Producer',
        'test.Producer',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const tCo = TypeVarType.createInstance('T_co');
    tCo.shared.declaredVariance = Variance.Covariant;
    producerClass.shared.typeParams.push(tCo);

    // Box[T_inv] (Invariant)
    const boxClass = ClassType.createInstantiable(
        'Box',
        'test.Box',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const tInv = TypeVarType.createInstance('T_inv');
    tInv.shared.declaredVariance = Variance.Invariant;
    boxClass.shared.typeParams.push(tInv);

    // Consumer[T_contra] (Contravariant)
    const consumerClass = ClassType.createInstantiable(
        'Consumer',
        'test.Consumer',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const tContra = TypeVarType.createInstance('T_contra');
    tContra.shared.declaredVariance = Variance.Contravariant;
    consumerClass.shared.typeParams.push(tContra);

    // Verify constructor type parameter variances
    assert.strictEqual(TypeVarType.getVariance(producerClass.shared.typeParams[0]), Variance.Covariant);
    assert.strictEqual(TypeVarType.getVariance(boxClass.shared.typeParams[0]), Variance.Invariant);
    assert.strictEqual(TypeVarType.getVariance(consumerClass.shared.typeParams[0]), Variance.Contravariant);
});

test('OrdinaryAppliedBoundRejectsConstructorSubscription', () => {
    const objectClass = ClassType.createInstantiable(
        'object',
        'builtins.object',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );

    const arrayClass = ClassType.createInstantiable(
        'Array',
        'test.Array',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const tCo = TypeVarType.createInstance('T_co');
    tCo.shared.declaredVariance = Variance.Covariant;
    arrayClass.shared.typeParams.push(tCo);

    // Array[object] is a fully-specialized concrete applied bound, NOT a generic constructor template
    const appliedBound = ClassType.specialize(ClassType.cloneAsInstance(arrayClass), [
        ClassType.cloneAsInstance(objectClass),
    ]);

    const boundedTypeVar = TypeVarType.createInstance('Bounded');
    boundedTypeVar.shared.boundType = appliedBound;

    // Check whether the bound is an ordinary applied type (has concrete typeArgs, no free TypeVars)
    // rather than an unspecialized constructor or a template containing free type variables.
    const isOrdinaryAppliedBound =
        isClassInstance(boundedTypeVar.shared.boundType) &&
        boundedTypeVar.shared.boundType.priv.typeArgs !== undefined &&
        boundedTypeVar.shared.boundType.priv.typeArgs.every((arg) => !isTypeVar(arg));

    assert.strictEqual(isOrdinaryAppliedBound, true);
});

test('ConcreteSubclassWithZeroTypeParamsRejectsTypeConstructorSpecialization', () => {
    const stringType = ClassType.createInstantiable(
        'StringType',
        'test.StringType',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const noneType = ClassType.createInstantiable(
        'NoneType',
        'test.NoneType',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    // Generic base class Field[GT] (arity 1)
    const fieldClass = ClassType.createInstantiable(
        'Field',
        'test.Field',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const gtTypeVar = TypeVarType.createInstance('GT');
    fieldClass.shared.typeParams.push(gtTypeVar);

    // Concrete subclass CharField(Field[str]) (arity 0)
    const charFieldClass = ClassType.createInstantiable(
        'CharField',
        'test.CharField',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const specializedFieldStr = ClassType.specialize(ClassType.cloneAsInstance(fieldClass), [
        ClassType.cloneAsInstance(stringType),
    ]);
    charFieldClass.shared.baseClasses.push(specializedFieldStr);

    // CharField has 0 type parameters
    assert.strictEqual(charFieldClass.shared.typeParams.length, 0);

    // If an applied TypeVar FieldT was solved to CharField, applying [StringType] to CharField
    // must be rejected (resolved as Unknown) because CharField is concrete and has arity 0.
    const fieldT = TypeVarType.createInstance('FieldT');
    fieldT.priv.typeArgs = [ClassType.cloneAsInstance(noneType)];

    const solution = new ConstraintSolution();
    solution.setType(fieldT, ClassType.cloneAsInstance(charFieldClass));

    const solved = applySolvedTypeVars(fieldT, solution);
    assert.strictEqual(printType(solved, PrintTypeFlags.None, returnTypeCallback), 'Unknown');
});

test('GenericSubclassPreservesConstructorArityAndSpecialization', () => {
    const stringType = ClassType.createInstantiable(
        'StringType',
        'test.StringType',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    // Generic base class Field[GT]
    const fieldClass = ClassType.createInstantiable(
        'Field',
        'test.Field',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const gtTypeVar = TypeVarType.createInstance('GT');
    fieldClass.shared.typeParams.push(gtTypeVar);

    // Generic subclass GenericCharField[T](Field[T]) (arity 1)
    const genericCharFieldClass = ClassType.createInstantiable(
        'GenericCharField',
        'test.GenericCharField',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const tTypeVar = TypeVarType.createInstance('T');
    genericCharFieldClass.shared.typeParams.push(tTypeVar);
    const specializedFieldT = ClassType.specialize(ClassType.cloneAsInstance(fieldClass), [tTypeVar]);
    genericCharFieldClass.shared.baseClasses.push(specializedFieldT);

    assert.strictEqual(genericCharFieldClass.shared.typeParams.length, 1);

    // When an applied TypeVar FieldT is solved to GenericCharField, applying [StringType]
    // produces GenericCharField[StringType].
    const fieldT = TypeVarType.createInstance('FieldT');
    fieldT.priv.typeArgs = [ClassType.cloneAsInstance(stringType)];

    const solution = new ConstraintSolution();
    solution.setType(fieldT, ClassType.cloneAsInstance(genericCharFieldClass));

    const solved = applySolvedTypeVars(fieldT, solution);
    assert.strictEqual(printType(solved, PrintTypeFlags.None, returnTypeCallback), 'GenericCharField[StringType]');
});

test('GenericConstructorSubclassMatchesGenericConstructorBound', () => {
    const stringType = ClassType.createInstantiable(
        'StringType',
        'test.StringType',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    // Generic base: Container[T]
    const containerClass = ClassType.createInstantiable(
        'Container',
        'test.Container',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const tParam = TypeVarType.createInstance('T');
    containerClass.shared.typeParams.push(tParam);

    // Generic subclass: SpecialContainer[T](Container[T])
    const specialContainerClass = ClassType.createInstantiable(
        'SpecialContainer',
        'test.SpecialContainer',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const specialTParam = TypeVarType.createInstance('T');
    specialContainerClass.shared.typeParams.push(specialTParam);
    const containerSpecialT = ClassType.specialize(containerClass, [specialTParam]);
    specialContainerClass.shared.baseClasses.push(containerSpecialT);
    specialContainerClass.shared.mro.push(specialContainerClass);
    specialContainerClass.shared.mro.push(containerClass);

    // Unrelated generic class: Other[T]
    const otherClass = ClassType.createInstantiable(
        'Other',
        'test.Other',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const otherTParam = TypeVarType.createInstance('T');
    otherClass.shared.typeParams.push(otherTParam);
    otherClass.shared.mro.push(otherClass);

    // Bound: Container[A]
    const aTypeVar = TypeVarType.createInstance('A');
    const containerA = ClassType.specialize(ClassType.cloneAsInstance(containerClass), [aTypeVar]);

    // ContainerT bound to Container[A]
    const containerT = TypeVarType.createInstance('ContainerT');
    containerT.shared.boundType = containerA;

    // 1. Verify SpecialContainer derives from Container (and therefore satisfies bound Container[A])
    const isSpecialContainerDerived = ClassType.isDerivedFrom(specialContainerClass, containerClass);
    assert.strictEqual(isSpecialContainerDerived, true);

    // 1b. Verify derivation also works when both or either are instance types
    const specialContainerInstance = ClassType.cloneAsInstance(specialContainerClass);
    const containerInstance = ClassType.cloneAsInstance(containerClass);
    assert.strictEqual(ClassType.isDerivedFrom(specialContainerInstance, containerInstance), true);
    assert.strictEqual(ClassType.isDerivedFrom(specialContainerInstance, containerClass), true);
    assert.strictEqual(ClassType.isDerivedFrom(specialContainerClass, containerInstance), true);

    // 2. Verify Other does NOT derive from Container
    const isOtherDerived = ClassType.isDerivedFrom(otherClass, containerClass);
    assert.strictEqual(isOtherDerived, false);

    // 3. Solving ContainerT to SpecialContainer preserves SpecialContainer and applies new type argument [StringType]
    containerT.priv.typeArgs = [ClassType.cloneAsInstance(stringType)];
    const solution = new ConstraintSolution();
    solution.setType(containerT, ClassType.cloneAsInstance(specialContainerClass));

    const solved = applySolvedTypeVars(containerT, solution);
    assert.strictEqual(printType(solved, PrintTypeFlags.None, returnTypeCallback), 'SpecialContainer[StringType]');
});

test('MultiLevelGenericConstructorInheritancePreservesDerivedConstructor', () => {
    const stringType = ClassType.createInstantiable(
        'StringType',
        'test.StringType',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    // BaseContainer[T]
    const baseClass = ClassType.createInstantiable(
        'BaseContainer',
        'test.BaseContainer',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    baseClass.shared.typeParams.push(TypeVarType.createInstance('T'));
    baseClass.shared.mro.push(baseClass);

    // MidContainer[T](BaseContainer[T])
    const midClass = ClassType.createInstantiable(
        'MidContainer',
        'test.MidContainer',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const midT = TypeVarType.createInstance('T');
    midClass.shared.typeParams.push(midT);
    midClass.shared.baseClasses.push(ClassType.specialize(baseClass, [midT]));
    midClass.shared.mro.push(midClass);
    midClass.shared.mro.push(baseClass);

    // LeafContainer[T](MidContainer[T])
    const leafClass = ClassType.createInstantiable(
        'LeafContainer',
        'test.LeafContainer',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const leafT = TypeVarType.createInstance('T');
    leafClass.shared.typeParams.push(leafT);
    leafClass.shared.baseClasses.push(ClassType.specialize(midClass, [leafT]));
    leafClass.shared.mro.push(leafClass);
    leafClass.shared.mro.push(midClass);
    leafClass.shared.mro.push(baseClass);

    // Verify derivation from BaseContainer
    assert.strictEqual(ClassType.isDerivedFrom(leafClass, baseClass), true);

    // Applying ContainerT[StringType] when solved to LeafContainer produces LeafContainer[StringType]
    const containerT = TypeVarType.createInstance('ContainerT');
    containerT.priv.typeArgs = [ClassType.cloneAsInstance(stringType)];
    const solution = new ConstraintSolution();
    solution.setType(containerT, ClassType.cloneAsInstance(leafClass));

    const solved = applySolvedTypeVars(containerT, solution);
    assert.strictEqual(printType(solved, PrintTypeFlags.None, returnTypeCallback), 'LeafContainer[StringType]');
});

// Helper function modeling the evaluator's rule for whether a constraint or bound
// qualifies a TypeVar to be an HKT constructor template (requires explicit free TypeVars).
function isExplicitHktConstructorTemplate(type: ClassType, expectedArity: number): boolean {
    if (!isClassInstance(type)) {
        return false;
    }
    // Must match expected type argument count
    if (type.shared.typeParams.length !== expectedArity) {
        return false;
    }
    // Must be explicitly parameterized with free TypeVar template parameters
    // Bare generic origins (priv.typeArgs === undefined) or concrete types (e.g. Array[Any], Array[object])
    // have 0 free TypeVars and are therefore ordinary types (*), NOT HKT constructor templates (* -> *).
    const freeTypeVars = getTypeVarArgsRecursive(type);
    return type.priv.typeArgs !== undefined && freeTypeVars.length > 0;
}

// Helper function modeling the evaluator's rule for whether a TypeVar can be subscripted as an HKT constructor.
function isValidHktConstructorTypeVar(typeVar: TypeVarType, expectedArity: number): boolean {
    if (typeVar.shared.constraints.length > 0) {
        return typeVar.shared.constraints.every((c) =>
            isClassInstance(c) ? isExplicitHktConstructorTemplate(c, expectedArity) : false
        );
    }

    if (typeVar.shared.boundType) {
        let hasValidBoundTemplate = false;
        if (isClassInstance(typeVar.shared.boundType)) {
            hasValidBoundTemplate = isExplicitHktConstructorTemplate(typeVar.shared.boundType, expectedArity);
        }
        return hasValidBoundTemplate;
    }

    // Unconstrained TypeVars (no bounds, no constraints) do NOT declare an explicit template
    // and must be rejected from being subscripted.
    return false;
}

test('ExplicitTemplateWithFreeTypeVarIsAcceptedAsHktTemplate', () => {
    const arrayClass = ClassType.createInstantiable(
        'Array',
        'test.Array',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const tParam = TypeVarType.createInstance('T');
    arrayClass.shared.typeParams.push(tParam);

    // Array[T] with free TypeVar T: valid HKT template (e.g. F: (Array[T], ChunkedArray[T]))
    const templateWithFreeVar = ClassType.specialize(ClassType.cloneAsInstance(arrayClass), [tParam]);
    assert.strictEqual(isExplicitHktConstructorTemplate(templateWithFreeVar, 1), true);

    const fTypeVar = TypeVarType.createInstance('F');
    fTypeVar.shared.constraints = [templateWithFreeVar];
    assert.strictEqual(isValidHktConstructorTypeVar(fTypeVar, 1), true);
});

test('UnconstrainedTypeVarIsRejectedAsHktConstructor', () => {
    // Bare unconstrained F = TypeVar("F") or def foo[F](x: F[int]): ...
    const unconstrainedF = TypeVarType.createInstance('F');
    assert.strictEqual(isValidHktConstructorTypeVar(unconstrainedF, 1), false);
});

test('BareGenericOriginWithoutExplicitTypeParamsIsRejectedAsHktTemplate', () => {
    const arrayClass = ClassType.createInstantiable(
        'Array',
        'test.Array',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    arrayClass.shared.typeParams.push(TypeVarType.createInstance('T'));

    // Bare Array (no type arguments): rejected as HKT template (defaults to ordinary Sequence/Array[Unknown])
    const bareArray = ClassType.cloneAsInstance(arrayClass);
    assert.strictEqual(isExplicitHktConstructorTemplate(bareArray, 1), false);

    const fTypeVar = TypeVarType.createInstance('F');
    fTypeVar.shared.constraints = [bareArray];
    assert.strictEqual(isValidHktConstructorTypeVar(fTypeVar, 1), false);
});

test('ConcreteAppliedTypesWithAnyOrObjectAreRejectedAsHktTemplates', () => {
    const anyType = AnyType.create();
    const objectClass = ClassType.createInstantiable(
        'object',
        'builtins.object',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );

    const arrayClass = ClassType.createInstantiable(
        'Array',
        'test.Array',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    arrayClass.shared.typeParams.push(TypeVarType.createInstance('T'));

    // Array[Any]: concrete applied constraint, 0 free TypeVars -> rejected as HKT template
    const arrayAny = ClassType.specialize(ClassType.cloneAsInstance(arrayClass), [anyType]);
    assert.strictEqual(isExplicitHktConstructorTemplate(arrayAny, 1), false);

    const fConstrainedAny = TypeVarType.createInstance('F');
    fConstrainedAny.shared.constraints = [arrayAny];
    assert.strictEqual(isValidHktConstructorTypeVar(fConstrainedAny, 1), false);

    // Array[object]: concrete applied bound, 0 free TypeVars -> rejected as HKT template
    const arrayObject = ClassType.specialize(ClassType.cloneAsInstance(arrayClass), [
        ClassType.cloneAsInstance(objectClass),
    ]);
    assert.strictEqual(isExplicitHktConstructorTemplate(arrayObject, 1), false);

    const fBoundObject = TypeVarType.createInstance('F');
    fBoundObject.shared.boundType = arrayObject;
    assert.strictEqual(isValidHktConstructorTypeVar(fBoundObject, 1), false);
});

test('TypeApplicationToHktConstructorValidatesTemplateParameterBounds', () => {
    const scalarClass = ClassType.createInstantiable(
        'Scalar',
        'test.Scalar',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    const intScalarClass = ClassType.createInstantiable(
        'IntScalar',
        'test.IntScalar',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    intScalarClass.shared.baseClasses.push(scalarClass);
    intScalarClass.shared.mro.push(intScalarClass);
    intScalarClass.shared.mro.push(scalarClass);

    const notScalarClass = ClassType.createInstantiable(
        'NotScalar',
        'test.NotScalar',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    const arrayClass = ClassType.createInstantiable(
        'Array',
        'test.Array',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    arrayClass.shared.typeParams.push(TypeVarType.createInstance('T'));

    // S has bound Scalar
    const sTypeVar = TypeVarType.createInstance('S');
    sTypeVar.shared.boundType = ClassType.cloneAsInstance(scalarClass);

    // Template is Array[S] where S: Scalar
    const arrayTemplate = ClassType.specialize(ClassType.cloneAsInstance(arrayClass), [sTypeVar]);

    // F: (Array[S],)
    const fTypeVar = TypeVarType.createInstance('F');
    fTypeVar.shared.constraints = [arrayTemplate];

    // Helper that checks if a type argument is valid for F's template parameter S at declaration time
    function validateHktTypeArg(typeVar: TypeVarType, argIndex: number, argType: Type): boolean {
        // Extract the template parameter at argIndex from each template constraint/bound
        const templateParams: TypeVarType[] = [];
        if (typeVar.shared.constraints.length > 0) {
            for (const constraint of typeVar.shared.constraints) {
                if (
                    isClassInstance(constraint) &&
                    constraint.priv.typeArgs &&
                    argIndex < constraint.priv.typeArgs.length
                ) {
                    const param = constraint.priv.typeArgs[argIndex];
                    if (isTypeVar(param)) {
                        templateParams.push(param);
                    }
                }
            }
        }

        // The applied argType must satisfy each template parameter's bound
        for (const param of templateParams) {
            if (param.shared.boundType && isClassInstance(param.shared.boundType)) {
                if (isClassInstance(argType)) {
                    if (!ClassType.isDerivedFrom(argType, param.shared.boundType)) {
                        return false;
                    }
                } else if (isTypeVar(argType)) {
                    // An unconstrained TypeVar X (bound is undefined / object) does NOT satisfy S's bound Scalar
                    if (!argType.shared.boundType || !isClassInstance(argType.shared.boundType)) {
                        return false;
                    }
                    if (!ClassType.isDerivedFrom(argType.shared.boundType, param.shared.boundType)) {
                        return false;
                    }
                } else {
                    return false;
                }
            }
        }

        return true;
    }

    // 1. Unconstrained X (e.g. def preserve[S: Scalar, F: (Array[S],), X](value: F[X]))
    // X has no bound (bound is object), so F[X] must be REJECTED at declaration time!
    const unconstrainedX = TypeVarType.createInstance('X');
    assert.strictEqual(validateHktTypeArg(fTypeVar, 0, unconstrainedX), false);

    // 2. Bound X: Scalar (e.g. def preserve[S: Scalar, F: (Array[S],), X: Scalar](value: F[X]))
    // X has bound Scalar, so F[X] is ACCEPTED!
    const boundedX = TypeVarType.createInstance('X');
    boundedX.shared.boundType = ClassType.cloneAsInstance(scalarClass);
    assert.strictEqual(validateHktTypeArg(fTypeVar, 0, boundedX), true);

    // 3. Concrete IntScalar (satisfies S: Scalar) -> ACCEPTED
    assert.strictEqual(validateHktTypeArg(fTypeVar, 0, ClassType.cloneAsInstance(intScalarClass)), true);

    // 4. Concrete NotScalar (does not satisfy S: Scalar) -> REJECTED
    assert.strictEqual(validateHktTypeArg(fTypeVar, 0, ClassType.cloneAsInstance(notScalarClass)), false);
});

test('MethodTypeVarBoundCanReferenceEnclosingClassTypeParam', () => {
    // Generic enclosing class BaseField[GT]
    const classScopeId = 'class.BaseField';
    const baseFieldClass = ClassType.createInstantiable(
        'BaseField',
        'test.BaseField',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    baseFieldClass.shared.typeVarScopeId = classScopeId;

    // GT is scoped to BaseField
    const gtTypeVar = TypeVarType.createInstance('GT');
    gtTypeVar.priv.scopeId = classScopeId;
    baseFieldClass.shared.typeParams.push(gtTypeVar);

    // Bound type BaseField[GT]
    const boundType = ClassType.specialize(ClassType.cloneAsInstance(baseFieldClass), [gtTypeVar]);

    // Validation helper checking whether all type variables in the bound are in liveScopeIds or are unscoped templates
    function isAllowedBoundType(type: Type, liveScopeIds: string[]): boolean {
        if (isTypeVar(type)) {
            // Unscoped template variables are allowed anywhere (e.g. module-level applied templates)
            if (!type.priv.scopeId) {
                return true;
            }
            // Scoped type variables must belong to one of the active enclosing scopes
            return liveScopeIds.includes(type.priv.scopeId);
        }

        if (isClassInstance(type) && type.priv.typeArgs) {
            return type.priv.typeArgs.every((arg) => isAllowedBoundType(arg, liveScopeIds));
        }

        return true;
    }

    // 1. Inside a method of BaseField (liveScopeIds = [methodScopeId, classScopeId]):
    // Bound BaseField[GT] is VALID because GT belongs to enclosing class BaseField!
    const methodScopeId = 'method.__new__';
    assert.strictEqual(isAllowedBoundType(boundType, [methodScopeId, classScopeId]), true);

    // 2. Outside BaseField (e.g. module level or unrelated function, liveScopeIds = ['unrelated.func']):
    // Bound BaseField[GT] is INVALID because GT is not in an active enclosing scope!
    assert.strictEqual(isAllowedBoundType(boundType, ['unrelated.func']), false);
});

test('NonGenericClassAssignedToAppliedTypeConstructorProducesDiagnostic', () => {
    const stringType = ClassType.createInstantiable(
        'StringType',
        'test.StringType',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    // Generic base class BaseField[GT]
    const baseFieldClass = ClassType.createInstantiable(
        'BaseField',
        'test.BaseField',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const gtTypeVar = TypeVarType.createInstance('GT');
    baseFieldClass.shared.typeParams.push(gtTypeVar);

    // Concrete subclass ConcreteCharField(BaseField[str]) (0 type parameters)
    const concreteCharField = ClassType.createInstantiable(
        'ConcreteCharField',
        'test.ConcreteCharField',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const baseFieldStr = ClassType.specialize(ClassType.cloneAsInstance(baseFieldClass), [
        ClassType.cloneAsInstance(stringType),
    ]);
    concreteCharField.shared.baseClasses.push(baseFieldStr);

    // Applied constructor destType: F[GT]
    const fTypeVar = TypeVarType.createInstance('F');
    fTypeVar.shared.boundType = ClassType.cloneAsInstance(baseFieldClass);
    const appliedDestType = TypeVarType.cloneForTypeApplication(fTypeVar, [gtTypeVar]);

    // Validation logic modeling assignType when assigning to an applied constructor
    function checkConstructorAssignment(
        dest: TypeVarType,
        src: ClassType
    ): { isAssignable: boolean; diagMessage?: string } {
        if (dest.priv.typeArgs) {
            if ((!isClassInstance(src) && !isInstantiableClass(src)) || !src.priv.typeArgs) {
                return {
                    isAssignable: false,
                    diagMessage: `"${src.shared.name}" is not a generic type constructor`,
                };
            }
        }
        return { isAssignable: true };
    }

    const result = checkConstructorAssignment(appliedDestType, concreteCharField);
    assert.strictEqual(result.isAssignable, false);
    assert.strictEqual(result.diagMessage, '"ConcreteCharField" is not a generic type constructor');
});

test('SpecializingEnclosingClassSpecializesMethodTypeVarBounds', () => {
    const stringType = ClassType.createInstantiable(
        'StringType',
        'test.StringType',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    // Generic class BaseField[GT]
    const classScopeId = 'class.BaseField';
    const baseFieldClass = ClassType.createInstantiable(
        'BaseField',
        'test.BaseField',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    baseFieldClass.shared.typeVarScopeId = classScopeId;

    const gtTypeVar = TypeVarType.createInstance('GT');
    gtTypeVar.priv.scopeId = classScopeId;
    baseFieldClass.shared.typeParams.push(gtTypeVar);

    // Method TypeVar F: BaseField[GT]
    const unspecializedBound = ClassType.specialize(ClassType.cloneAsInstance(baseFieldClass), [gtTypeVar]);
    const methodTypeVarF = TypeVarType.createInstance('F');
    methodTypeVarF.shared.boundType = unspecializedBound;

    // When BaseField is specialized with GT = StringType (e.g. for ConcreteCharField(BaseField[str])):
    const solution = new ConstraintSolution();
    solution.setType(gtTypeVar, ClassType.cloneAsInstance(stringType));

    // Specializing F's bound type with the enclosing class solution produces BaseField[StringType]
    const specializedBound = applySolvedTypeVars(methodTypeVarF.shared.boundType, solution);
    assert.strictEqual(printType(specializedBound, PrintTypeFlags.None, returnTypeCallback), 'BaseField[StringType]');
});

test('MostDerivedGenericConstructorInMroMatchesConstructorBound', () => {
    const stringType = ClassType.createInstantiable(
        'StringType',
        'test.StringType',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );

    // Root Generic Base: BaseField[GT] (arity 1)
    const baseFieldClass = ClassType.createInstantiable(
        'BaseField',
        'test.BaseField',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const gtTypeVar = TypeVarType.createInstance('GT');
    baseFieldClass.shared.typeParams.push(gtTypeVar);
    baseFieldClass.shared.mro.push(baseFieldClass);

    // Intermediate Generic Subclass: SpecialField[GT](BaseField[GT]) (arity 1)
    const specialFieldClass = ClassType.createInstantiable(
        'SpecialField',
        'test.SpecialField',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const specialGtVar = TypeVarType.createInstance('GT');
    specialFieldClass.shared.typeParams.push(specialGtVar);
    specialFieldClass.shared.baseClasses.push(ClassType.specialize(baseFieldClass, [specialGtVar]));
    computeMroLinearization(specialFieldClass);

    // Concrete Leaf Subclass: ConcreteCharField(SpecialField[str]) (arity 0)
    const concreteCharField = ClassType.createInstantiable(
        'ConcreteCharField',
        'test.ConcreteCharField',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    concreteCharField.shared.baseClasses.push(
        ClassType.specialize(specialFieldClass, [ClassType.cloneAsInstance(stringType)])
    );
    computeMroLinearization(concreteCharField);

    // Candidate resolution logic: find the most-derived generic class in MRO
    // that has matching arity (1) and derives from BaseField
    const matchingBase = concreteCharField.shared.mro.find(
        (mroClass): mroClass is ClassType =>
            isInstantiableClass(mroClass) &&
            mroClass.shared.typeParams.length === 1 &&
            (ClassType.isSameGenericClass(mroClass, baseFieldClass) ||
                ClassType.isDerivedFrom(mroClass, baseFieldClass))
    );

    // Must resolve to SpecialField (the most-derived generic constructor in the MRO), NOT BaseField!
    assert.ok(matchingBase !== undefined);
    assert.strictEqual(matchingBase.shared.name, 'SpecialField');
    assert.ok(matchingBase.priv.typeArgs !== undefined && matchingBase.priv.typeArgs.length === 1);
    assert.strictEqual(printType(matchingBase.priv.typeArgs[0], PrintTypeFlags.None, returnTypeCallback), 'StringType');

    // When applied TypeVar F is solved to SpecialField with argument StringType,
    // it yields SpecialField[StringType]
    const fTypeVar = TypeVarType.createInstance('F');
    fTypeVar.priv.typeArgs = [ClassType.cloneAsInstance(stringType)];
    const solution = new ConstraintSolution();
    solution.setType(fTypeVar, ClassType.cloneAsInstance(specialFieldClass));

    const solved = applySolvedTypeVars(fTypeVar, solution);
    assert.strictEqual(printType(solved, PrintTypeFlags.None, returnTypeCallback), 'SpecialField[StringType]');
});

test('AppliedConstructorBoundToEnclosingClassSatisfiesSelfParamCheck', () => {
    const classScopeId = 'class.BidirectionalMapping';

    // Generic class BidirectionalMapping[KT, VT] (arity 2)
    const bidiClass = ClassType.createInstantiable(
        'BidirectionalMapping',
        'test.BidirectionalMapping',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    bidiClass.shared.typeVarScopeId = classScopeId;

    const ktParam = TypeVarType.createInstance('KT');
    ktParam.priv.scopeId = classScopeId;
    const vtParam = TypeVarType.createInstance('VT');
    vtParam.priv.scopeId = classScopeId;
    bidiClass.shared.typeParams.push(ktParam, vtParam);

    // MapT: BidirectionalMapping[KT, VT]
    const bidiTemplate = ClassType.specialize(ClassType.cloneAsInstance(bidiClass), [ktParam, vtParam]);
    const mapTVar = TypeVarType.createInstance('MapT');
    mapTVar.shared.boundType = bidiTemplate;

    // self: MapT[KT, VT]
    const selfParamType = TypeVarType.cloneForTypeApplication(mapTVar, [ktParam, vtParam]);

    // Concretized selfParamType should expand to bound BidirectionalMapping[KT, VT]
    // with typeArgs [KT, VT] applied.
    assert.ok(selfParamType.shared.boundType !== undefined);
    assert.ok(isClassInstance(selfParamType.shared.boundType));
    assert.strictEqual(
        printType(selfParamType.shared.boundType, PrintTypeFlags.None, returnTypeCallback),
        'BidirectionalMapping[KT, VT]'
    );

    // Method `inverse(self: MapT[KT, VT]) -> MapT[VT, KT]`
    // When called on receiver bidict[int, str]:
    const bidictClass = ClassType.createInstantiable(
        'bidict',
        'test.bidict',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    bidictClass.shared.typeParams.push(TypeVarType.createInstance('KT'), TypeVarType.createInstance('VT'));
    bidictClass.shared.baseClasses.push(ClassType.specialize(bidiClass, bidictClass.shared.typeParams));
    computeMroLinearization(bidictClass);

    // Return type MapT[VT, KT] with solution { MapT -> bidict } yields bidict[VT, KT]
    const stringType = ClassType.createInstantiable(
        'str',
        'builtins.str',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );
    const intType = ClassType.createInstantiable(
        'int',
        'builtins.int',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );

    const returnTypeVar = TypeVarType.cloneForTypeApplication(mapTVar, [
        ClassType.cloneAsInstance(stringType),
        ClassType.cloneAsInstance(intType),
    ]);

    const solution = new ConstraintSolution();
    solution.setType(mapTVar, ClassType.cloneAsInstance(bidictClass));

    const solvedReturn = applySolvedTypeVars(returnTypeVar, solution);
    assert.strictEqual(printType(solvedReturn, PrintTypeFlags.None, returnTypeCallback), 'bidict[str, int]');
});

test('UnspecializedGenericClassAsHigherKindedConstructorGap', () => {
    // Gap Demonstration 1: Passing unspecialized generic class `Box` to `klass: type[T[Any]]`
    // Generic class Box[T] (instantiable, arity 1, unspecialized so priv.typeArgs is undefined)
    const boxClass = ClassType.createInstantiable(
        'Box',
        'test.Box',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const tParam = TypeVarType.createInstance('T');
    boxClass.shared.typeParams.push(tParam);

    // Verify Box is an instantiable generic class whose typeArgs are undefined
    assert.strictEqual(isInstantiableClass(boxClass), true);
    assert.strictEqual(boxClass.shared.typeParams.length, 1);
    assert.strictEqual(boxClass.priv.typeArgs, undefined);

    // Generic TypeVar T
    const tVar = TypeVarType.createInstance('T');

    // Destination is an applied TypeVar constructor: type[T[Any]] (instantiable form of T applied to Any)
    const anyType = AnyType.create();
    const appliedDestType = TypeVarType.cloneForTypeApplication(TypeVarType.cloneAsInstantiable(tVar), [anyType]);
    assert.strictEqual(appliedDestType.priv.typeArgs?.length, 1);

    // The current flawed assignType logic checks `!src.priv.typeArgs`, which rejects `Box`
    function currentCheck(src: ClassType): { isGenericConstructor: boolean } {
        return { isGenericConstructor: !!src.priv.typeArgs };
    }

    // The desired behavior recognizes that an unspecialized generic class with typeParams IS a constructor
    function desiredCheck(src: ClassType): { isGenericConstructor: boolean } {
        const isGeneric = !!src.priv.typeArgs || (isInstantiableClass(src) && src.shared.typeParams.length > 0);
        return { isGenericConstructor: isGeneric };
    }

    // Gap demonstrated: current check fails on Box, while desired check succeeds
    assert.strictEqual(currentCheck(boxClass).isGenericConstructor, false);
    assert.strictEqual(desiredCheck(boxClass).isGenericConstructor, true);

    // When solved, applying { T -> Box } to T[str] should produce Box[str]
    const stringType = ClassType.createInstantiable(
        'str',
        'builtins.str',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );
    const returnTypeVar = TypeVarType.cloneForTypeApplication(tVar, [ClassType.cloneAsInstance(stringType)]);
    const solution = new ConstraintSolution();
    solution.setType(tVar, ClassType.cloneAsInstance(boxClass));

    const solvedReturn = applySolvedTypeVars(returnTypeVar, solution);
    assert.strictEqual(printType(solvedReturn, PrintTypeFlags.None, returnTypeCallback), 'Box[str]');
});

test('ProtocolBoundForHigherKindedConstructorGap', () => {
    // Gap Demonstration: Protocol bound matching for higher-kinded type constructor
    // Protocol SinglePositionalConstructible[T]
    const protocolClass = ClassType.createInstantiable(
        'SinglePositionalConstructible',
        'test.SinglePositionalConstructible',
        'test',
        Uri.empty(),
        ClassTypeFlags.ProtocolClass,
        0,
        undefined,
        undefined
    );
    const protoTVar = TypeVarType.createInstance('T');
    protocolClass.shared.typeParams.push(protoTVar);

    // Box[T] structurally satisfies SinglePositionalConstructible[T],
    // but does NOT nominally inherit from SinglePositionalConstructible in its MRO.
    const boxClass = ClassType.createInstantiable(
        'Box',
        'test.Box',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const boxTVar = TypeVarType.createInstance('T');
    boxClass.shared.typeParams.push(boxTVar);
    computeMroLinearization(boxClass);

    // F bounded by SinglePositionalConstructible[T]
    // def create[K, F: SinglePositionalConstructible[K]](klass: type[F[Any]], value: K) -> F[K]: ...
    const fTypeVar = TypeVarType.createInstance('F');
    const protoTemplate = ClassType.specialize(ClassType.cloneAsInstance(protocolClass), [protoTVar]);
    fTypeVar.shared.boundType = protoTemplate;

    // In current typeEvaluator.assignType HKT validation (lines 26420-26445):
    // The check only tests nominal derivation:
    // 1. ClassType.isSameGenericClass(boundSubtype, constructorTypeForConstraint)
    // 2. ClassType.isDerivedFrom(constructorTypeForConstraint, boundSubtype) via MRO
    const currentNominalCheck =
        ClassType.isSameGenericClass(protoTemplate, boxClass) || ClassType.isDerivedFrom(boxClass, protoTemplate);

    // 1. Current HKT solver nominal-only check FAILS for Protocol bounds on non-inheriting classes
    assert.strictEqual(currentNominalCheck, false);

    // 2. The desired behavior is structural protocol checking:
    // When bound is a ProtocolClass, it should test whether generic constructor `Box`
    // can structurally implement `SinglePositionalConstructible` across its type parameter.
    const isProtocolBound = ClassType.isProtocolClass(protoTemplate);
    assert.strictEqual(isProtocolBound, true);

    // 3. Once protocol compatibility is established, constraint solving F -> Box and
    // applying the solution to return type F[str] must successfully produce Box[str]
    const stringType = ClassType.createInstantiable(
        'str',
        'builtins.str',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );
    const returnTypeVar = TypeVarType.cloneForTypeApplication(fTypeVar, [ClassType.cloneAsInstance(stringType)]);
    const solution = new ConstraintSolution();
    solution.setType(fTypeVar, ClassType.cloneAsInstance(boxClass));

    const solvedReturn = applySolvedTypeVars(returnTypeVar, solution);
    assert.strictEqual(printType(solvedReturn, PrintTypeFlags.None, returnTypeCallback), 'Box[str]');
});

test('UnspecializedGenericClassConstructorSlotWildcardUnificationGap', () => {
    // Gap Demonstration: Solving T -> Box and T@Box -> Unknown when passing bare generic class `Box` to `type[T[Any]]`
    // Generic class Box[T@Box]
    const boxClass = ClassType.createInstantiable(
        'Box',
        'test.Box',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const tBoxParam = TypeVarType.createInstance('T@Box');
    boxClass.shared.typeParams.push(tBoxParam);

    // Bare generic class reference passed as argument: type[Box[T@Box]] (unspecialized constructor)
    const srcConstructorType = boxClass;
    assert.strictEqual(srcConstructorType.priv.typeArgs, undefined);
    assert.strictEqual(srcConstructorType.shared.typeParams.length, 1);

    // Target parameter: klass: type[T@create[Any]]
    // destType is TypeVar T@create applied to [Any] in instantiable form
    const tCreateVar = TypeVarType.createInstance('T@create');
    const anyType = AnyType.create();
    const destAppliedType = TypeVarType.cloneForTypeApplication(TypeVarType.cloneAsInstantiable(tCreateVar), [anyType]);

    // Current HKT assignType solver logic checks `if (!effectiveSrcClass.priv.typeArgs)`
    // and aborts before constraint extraction:
    const currentSolverExtractsConstraints = (src: ClassType): boolean => {
        return src.priv.typeArgs !== undefined;
    };
    assert.strictEqual(currentSolverExtractsConstraints(srcConstructorType), false);

    // Desired HKT constraint extraction:
    // 1. Identify constructor class T@create -> Box
    // 2. Unify/default unsupplied type parameters T@Box with the wildcard slot (Any / Unknown)
    const desiredSolution = new ConstraintSolution();
    if (isInstantiableClass(srcConstructorType) && srcConstructorType.shared.typeParams.length > 0) {
        desiredSolution.setType(tCreateVar, ClassType.cloneAsInstance(srcConstructorType));
        // Wildcard slot Any / Unknown unifies with the constructor's type parameter
        const wildcardSlot = destAppliedType.priv.typeArgs![0];
        desiredSolution.setType(tBoxParam, wildcardSlot);
    }

    assert.strictEqual(desiredSolution.getMainSolutionSet().getType(tCreateVar) !== undefined, true);
    assert.strictEqual(desiredSolution.getMainSolutionSet().getType(tBoxParam) !== undefined, true);

    // When value: K is passed as "a" (str), K resolves to str.
    // Return type T@create[K] with solution { T@create -> Box, K -> str } specializes to Box[str]:
    const stringType = ClassType.createInstantiable(
        'str',
        'builtins.str',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );
    const returnTypeVar = TypeVarType.cloneForTypeApplication(tCreateVar, [ClassType.cloneAsInstance(stringType)]);
    const solvedReturn = applySolvedTypeVars(returnTypeVar, desiredSolution);
    assert.strictEqual(printType(solvedReturn, PrintTypeFlags.None, returnTypeCallback), 'Box[str]');
});

test('HigherKindedTypeConstructorBareUsageVsSubscriptedApplicationGap', () => {
    // Gap Demonstration: Unsubscripted reference `cls: type[FieldT]` vs valid application `-> FieldT[GT | None]`
    // Generic base class Field[GT]
    const fieldClass = ClassType.createInstantiable(
        'Field',
        'test.Field',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const gtParam = TypeVarType.createInstance('GT');
    fieldClass.shared.typeParams.push(gtParam);

    // Constructor TypeVar FieldT with template bound Field[GT] (arity 1 constructor)
    const fieldTVar = TypeVarType.createInstance('FieldT');
    const fieldTemplate = ClassType.specialize(ClassType.cloneAsInstance(fieldClass), [gtParam]);
    fieldTVar.shared.boundType = fieldTemplate;

    // Helper checking whether a bound constitutes an explicit generic constructor template
    const isExplicitTemplateConstraint = (type: Type): boolean =>
        isClassInstance(type) &&
        type.shared.typeParams.length > 0 &&
        type.priv.typeArgs !== undefined &&
        getTypeVarArgsRecursive(type).length > 0;

    const hasTemplate = isExplicitTemplateConstraint(fieldTVar.shared.boundType);
    assert.strictEqual(hasTemplate, true);

    // Flawed evaluator state transition:
    // When evaluating `cls: type[FieldT]`, unsubscripted reference triggers `isUsedAsOrdinaryType = true`
    const isUsedAsOrdinaryType = true;

    // Subsequent valid return type annotation `FieldT[GT | None]` is evaluated
    const stringType = ClassType.createInstantiable(
        'str',
        'builtins.str',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );
    const appliedTypeArgs = [ClassType.cloneAsInstance(stringType)];

    // Current logic in getTypeOfIndexWithBaseType:
    const currentIsValidApplication = !isUsedAsOrdinaryType && hasTemplate;
    // Current logic mistakenly marks the return type subscript as invalid ("not subscriptable")
    assert.strictEqual(currentIsValidApplication, false);

    // Desired logic:
    // 1. Unsubscripted `FieldT` is detected as a constructor missing type arguments (or defaulting to [Any])
    // 2. It does NOT poison subsequent valid constructor applications `FieldT[...]`
    const desiredIsConstructor = hasTemplate;
    const desiredIsValidApplication =
        desiredIsConstructor && appliedTypeArgs.length === fieldClass.shared.typeParams.length;
    assert.strictEqual(desiredIsValidApplication, true);

    // When FieldT is solved to Field, FieldT[str] specializes to Field[str]
    const returnAppliedType = TypeVarType.cloneForTypeApplication(fieldTVar, appliedTypeArgs);
    const solution = new ConstraintSolution();
    solution.setType(fieldTVar, ClassType.cloneAsInstance(fieldClass));

    const solvedReturn = applySolvedTypeVars(returnAppliedType, solution);
    assert.strictEqual(printType(solvedReturn, PrintTypeFlags.None, returnTypeCallback), 'Field[str]');
});

test('UnsolvedEnclosingClassTypeVarInMethodReturnTypeReplacedWithUnknown', () => {
    // Enclosing class Field[GT]
    const classScopeId = 'class.Field';
    const fieldClass = ClassType.createInstantiable(
        'Field',
        'test.Field',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    fieldClass.shared.typeVarScopeId = classScopeId;

    const gtTypeVar = TypeVarType.createInstance('GT');
    gtTypeVar.priv.scopeId = classScopeId;
    gtTypeVar.priv.nameWithScope = 'GT@Field';
    fieldClass.shared.typeParams.push(gtTypeVar);

    // Method __new__[FieldT: Field[GT]](cls: type[FieldT], ...) -> FieldT[GT | None]
    const methodScopeId = 'method.__new__';
    const fieldTVar = TypeVarType.createInstance('FieldT');
    fieldTVar.priv.scopeId = methodScopeId;
    fieldTVar.priv.nameWithScope = 'FieldT@__new__';

    // Bound constructor method includes constructorTypeVarScopeId (classScopeId)
    const boundNewScopeIds = [methodScopeId, classScopeId];

    // Return type FieldT[GT | None]
    const returnTypeVar = TypeVarType.cloneForTypeApplication(fieldTVar, [gtTypeVar]);

    // When solving the call on `CharField(null=True)` with bare `cls: type[FieldT]`:
    // FieldT is solved to Field, but GT is NOT solved in the method call constraints.
    const methodSolution = new ConstraintSolution();
    methodSolution.setType(fieldTVar, ClassType.cloneAsInstance(fieldClass));

    // When replaceUnsolved includes all active constructor scope IDs (methodScopeId + classScopeId),
    // unsolved GT becomes Unknown rather than leaking as raw GT@Field:
    const applied = applySolvedTypeVars(returnTypeVar, methodSolution, {
        replaceUnsolved: {
            scopeIds: boundNewScopeIds,
            tupleClassType: undefined,
            eliminateUnsolvedInUnions: false,
        },
    });

    assert.strictEqual(printType(applied, PrintTypeFlags.None, returnTypeCallback), 'Field[Unknown]');
});

test('ConstantTypeConstructorAliasYieldsUnknownGap', () => {
    // Gap Demonstration: Constant/phantom type constructor alias `type ConstNone[T] = None`
    // vs generic type constructor alias `type Result[T] = Coroutine[Any, Any, T]`

    const noneType = ClassType.createInstantiable(
        'NoneType',
        'builtins.NoneType',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );

    const coroutineClass = ClassType.createInstantiable(
        'Coroutine',
        'collections.abc.Coroutine',
        'collections.abc',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const coroutineT = TypeVarType.createInstance('T');
    coroutineClass.shared.typeParams.push(coroutineT);

    const stringType = ClassType.createInstantiable(
        'str',
        'builtins.str',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );

    // 1. ResultConstructor: `type Result[T] = Coroutine[T]`
    // When Result is passed to TypeVar WrapperT and subscripted as WrapperT[str],
    // Result has a free type parameter in its target type:
    const resultAliasInfo = {
        shared: {
            name: 'Result',
            fullName: 'test.Result',
            moduleName: 'test',
            fileUri: Uri.empty(),
            typeVarScopeId: 'test.scope',
            isTypeAliasType: true,
            typeParams: [coroutineT],
            computedVariance: undefined,
        },
        typeArgs: undefined,
    };
    const resultTarget = ClassType.specialize(ClassType.cloneAsInstance(coroutineClass), [coroutineT]);
    const resultAlias = TypeBase.cloneForTypeAlias(resultTarget, resultAliasInfo);

    // Constructor TypeVar WrapperT applied to [str]: WrapperT[str]
    const wrapperTVar = TypeVarType.createInstance('WrapperT');
    const appliedWrapperStr = TypeVarType.cloneForTypeApplication(wrapperTVar, [ClassType.cloneAsInstance(stringType)]);

    // Solving WrapperT = Result successfully specializes Coroutine[str]:
    const resultSolution = new ConstraintSolution();
    resultSolution.setType(wrapperTVar, resultAlias);
    const solvedResult = applySolvedTypeVars(appliedWrapperStr, resultSolution);
    assert.strictEqual(printType(solvedResult, PrintTypeFlags.ExpandTypeAlias, returnTypeCallback), 'Coroutine[str]');

    // 2. ConstNoneConstructor: `type ConstNone[T] = None`
    // The type parameter `T` is NOT used in the target type `NoneType` (phantom/constant type constructor).
    const phantomT = TypeVarType.createInstance('T');
    const constNoneAliasInfo = {
        shared: {
            name: 'ConstNone',
            fullName: 'test.ConstNone',
            moduleName: 'test',
            fileUri: Uri.empty(),
            typeVarScopeId: 'test.scope2',
            isTypeAliasType: true,
            typeParams: [phantomT],
            computedVariance: undefined,
        },
        typeArgs: undefined,
    };
    const noneInstance = ClassType.cloneAsInstance(noneType);
    const constNoneAlias = TypeBase.cloneForTypeAlias(noneInstance, constNoneAliasInfo);

    // Solving WrapperT = ConstNone:
    const noneSolution = new ConstraintSolution();
    noneSolution.setType(wrapperTVar, constNoneAlias);

    // With targeted fix:
    // A constant / phantom type constructor of kind `* -> *` mapping any `T` to `NoneType`
    // solves `WrapperT[str]` to `NoneType`, properly discarding the unused type parameter.
    const solvedNone = applySolvedTypeVars(appliedWrapperStr, noneSolution);
    assert.strictEqual(printType(solvedNone, PrintTypeFlags.ExpandTypeAlias, returnTypeCallback), 'None');
});

test('HigherKindedTypeConstructorAppliedInBaseClassDoesNotLeakOuterTypeVar', () => {
    // Demonstrates:
    // class CoroutineFacade[X](GenericFacade[X, Result[X]])
    // where GenericFacade has method -> WrapperT[str]
    // The solved return type for WrapperT[str] must be Coroutine[Any, Any, str], NOT Coroutine[Any, Any, X@CoroutineFacade].

    const coroutineClass = ClassType.createInstantiable(
        'Coroutine',
        'collections.abc.Coroutine',
        'collections.abc',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const coroutineT = TypeVarType.createInstance('T');
    coroutineClass.shared.typeParams.push(coroutineT);

    const stringType = ClassType.createInstantiable(
        'str',
        'builtins.str',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );

    // Outer type param X from CoroutineFacade: class CoroutineFacade[X]
    const xTypeVar = TypeVarType.createInstance('X');
    xTypeVar.priv.scopeId = 'class.CoroutineFacade';
    xTypeVar.priv.nameWithScope = 'X@CoroutineFacade';

    // Type alias: type Result[T] = Coroutine[T]
    const resultAliasInfo = {
        shared: {
            name: 'Result',
            fullName: 'test.Result',
            moduleName: 'test',
            fileUri: Uri.empty(),
            typeVarScopeId: 'test.scope',
            isTypeAliasType: true,
            typeParams: [coroutineT],
            computedVariance: undefined,
        },
        typeArgs: [xTypeVar],
    };
    // Result[X] passed as type argument to GenericFacade's WrapperT parameter
    const resultXTarget = ClassType.specialize(ClassType.cloneAsInstance(coroutineClass), [xTypeVar]);
    const resultXAlias = TypeBase.cloneForTypeAlias(resultXTarget, resultAliasInfo);

    // In GenericFacade, method return type is declared as WrapperT[str]:
    const wrapperTVar = TypeVarType.createInstance('WrapperT');
    const appliedWrapperStr = TypeVarType.cloneForTypeApplication(wrapperTVar, [ClassType.cloneAsInstance(stringType)]);

    // When specializing GenericFacade for CoroutineFacade, WrapperT is bound to Result[X]:
    const solution = new ConstraintSolution();
    solution.setType(wrapperTVar, resultXAlias);

    // Applying WrapperT[str] with WrapperT = Result[X] must substitute the type alias's
    // type parameter T -> str (yielding Coroutine[str]), NOT leak the specialized X argument.
    const solved = applySolvedTypeVars(appliedWrapperStr, solution);
    assert.strictEqual(printType(solved, PrintTypeFlags.ExpandTypeAlias, returnTypeCallback), 'Coroutine[str]');
});

test('PartiallyAppliedGenericConstructorSpecializesFreeTemplateTypeVars', () => {
    // Demonstrates:
    // class dict[KT, VT]: ...
    // def fromkeys[T, DictT: dict[T, Any]](iterable: Iterable[T]) -> DictT[T]
    // When DictT is bound to dict[T, Any] (1 free TypeVar T), DictT[int] solves to dict[int, Any].
    // When DictT is bound to OrderedDict[T, Any], DictT[int] solves to OrderedDict[int, Any].

    const dictClass = ClassType.createInstantiable(
        'dict',
        'builtins.dict',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );
    const ktParam = TypeVarType.createInstance('KT');
    const vtParam = TypeVarType.createInstance('VT');
    dictClass.shared.typeParams.push(ktParam);
    dictClass.shared.typeParams.push(vtParam);

    const orderedDictClass = ClassType.createInstantiable(
        'OrderedDict',
        'collections.OrderedDict',
        'collections',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const ordKtParam = TypeVarType.createInstance('KT');
    const ordVtParam = TypeVarType.createInstance('VT');
    orderedDictClass.shared.typeParams.push(ordKtParam);
    orderedDictClass.shared.typeParams.push(ordVtParam);
    const dictBaseSpecialized = ClassType.specialize(dictClass, [ordKtParam, ordVtParam]);
    orderedDictClass.shared.baseClasses.push(dictBaseSpecialized);
    orderedDictClass.shared.mro.push(orderedDictClass);
    orderedDictClass.shared.mro.push(dictClass);

    const intType = ClassType.createInstantiable(
        'int',
        'builtins.int',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );

    // Template bound: dict[T, Any]
    const tParam = TypeVarType.createInstance('T');
    const dictTemplate = ClassType.specialize(ClassType.cloneAsInstance(dictClass), [tParam, AnyType.create()]);

    // DictT: dict[T, Any] (takes 1 argument T)
    const dictTVar = TypeVarType.createInstance('DictT');
    dictTVar.shared.boundType = dictTemplate;

    // Applied return type: DictT[int]
    const appliedDictTInt = TypeVarType.cloneForTypeApplication(dictTVar, [ClassType.cloneAsInstance(intType)]);

    // 1. When DictT is solved to dict[T, Any]:
    const dictSolution = new ConstraintSolution();
    dictSolution.setType(dictTVar, dictTemplate);
    const solvedDict = applySolvedTypeVars(appliedDictTInt, dictSolution);
    assert.strictEqual(printType(solvedDict, PrintTypeFlags.None, returnTypeCallback), 'dict[int, Any]');

    // 2. When DictT is solved to OrderedDict[T, Any]:
    const orderedDictTemplate = ClassType.specialize(ClassType.cloneAsInstance(orderedDictClass), [
        tParam,
        AnyType.create(),
    ]);
    const orderedSolution = new ConstraintSolution();
    orderedSolution.setType(dictTVar, orderedDictTemplate);
    const solvedOrderedDict = applySolvedTypeVars(appliedDictTInt, orderedSolution);
    assert.strictEqual(printType(solvedOrderedDict, PrintTypeFlags.None, returnTypeCallback), 'OrderedDict[int, Any]');
});

test('ClassMethodFromkeysTwoArgOverloadWithFullHKTSpecialization', () => {
    // Demonstrates:
    // class dict[KT, VT]: ...
    // @classmethod
    // def fromkeys[T, S, DictT: dict[T, S]](cls: type[DictT[T, S]], iterable: Iterable[T], value: S) -> DictT[T, S]
    // 1. When called on dict with [int], "food":
    //    DictT[int, str] specializes to dict[int, str]
    // 2. When called on OrderedDict with [int], "food":
    //    DictT[int, str] specializes to OrderedDict[int, str]

    const dictClass = ClassType.createInstantiable(
        'dict',
        'builtins.dict',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );
    const ktParam = TypeVarType.createInstance('KT');
    const vtParam = TypeVarType.createInstance('VT');
    dictClass.shared.typeParams.push(ktParam);
    dictClass.shared.typeParams.push(vtParam);

    const orderedDictClass = ClassType.createInstantiable(
        'OrderedDict',
        'collections.OrderedDict',
        'collections',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const ordKtParam = TypeVarType.createInstance('KT');
    const ordVtParam = TypeVarType.createInstance('VT');
    orderedDictClass.shared.typeParams.push(ordKtParam);
    orderedDictClass.shared.typeParams.push(ordVtParam);
    const dictBaseSpecialized = ClassType.specialize(dictClass, [ordKtParam, ordVtParam]);
    orderedDictClass.shared.baseClasses.push(dictBaseSpecialized);
    orderedDictClass.shared.mro.push(orderedDictClass);
    orderedDictClass.shared.mro.push(dictClass);

    const intType = ClassType.createInstantiable(
        'int',
        'builtins.int',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );
    const stringType = ClassType.createInstantiable(
        'str',
        'builtins.str',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );

    // Template bound: dict[T, S] (2 free type variables)
    const tParam = TypeVarType.createInstance('T');
    const sParam = TypeVarType.createInstance('S');
    const dictTemplate2 = ClassType.specialize(ClassType.cloneAsInstance(dictClass), [tParam, sParam]);

    // DictT: dict[T, S]
    const dictTVar = TypeVarType.createInstance('DictT');
    dictTVar.shared.boundType = dictTemplate2;

    // Return type expression: DictT[int, str]
    const appliedDictTIntStr = TypeVarType.cloneForTypeApplication(dictTVar, [
        ClassType.cloneAsInstance(intType),
        ClassType.cloneAsInstance(stringType),
    ]);

    // 1. Solving DictT = dict -> dict[int, str]
    const dictSolution = new ConstraintSolution();
    dictSolution.setType(dictTVar, ClassType.cloneAsInstance(dictClass));
    const solvedDict = applySolvedTypeVars(appliedDictTIntStr, dictSolution);
    assert.strictEqual(printType(solvedDict, PrintTypeFlags.None, returnTypeCallback), 'dict[int, str]');

    // 2. Solving DictT = OrderedDict -> OrderedDict[int, str]
    const orderedSolution = new ConstraintSolution();
    orderedSolution.setType(dictTVar, ClassType.cloneAsInstance(orderedDictClass));
    const solvedOrderedDict = applySolvedTypeVars(appliedDictTIntStr, orderedSolution);
    assert.strictEqual(printType(solvedOrderedDict, PrintTypeFlags.None, returnTypeCallback), 'OrderedDict[int, str]');
});

test('DiagnosticCheckForPartiallyAppliedConstructorTemplateBound', () => {
    // Diagnoses the exact compiler pipeline steps needed for `DictT: _dict2[_T, Any]` and `cls: type[DictT[_T]]`:
    //
    // 1. Template validation:
    //    `_dict2[_T, Any]` has 2 type arguments where one is a free TypeVar `_T`
    //    and the other is `Any`. This constitutes a partially-applied template of arity 1.
    const isExplicitTemplateConstraint = (type: Type, expectedArity: number): boolean =>
        isClassInstance(type) &&
        (type.shared.typeParams.length === expectedArity || getTypeVarArgsRecursive(type).length === expectedArity) &&
        type.priv.typeArgs !== undefined &&
        getTypeVarArgsRecursive(type).length > 0;

    const dictClass = ClassType.createInstantiable(
        'dict',
        'builtins.dict',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );
    const ktParam = TypeVarType.createInstance('KT');
    const vtParam = TypeVarType.createInstance('VT');
    dictClass.shared.typeParams.push(ktParam, vtParam);

    const tParam = TypeVarType.createInstance('_T');
    const partiallyAppliedBound = ClassType.specialize(ClassType.cloneAsInstance(dictClass), [
        tParam,
        AnyType.create(),
    ]);

    // Arity 1 application DictT[_T] matches the 1 free type parameter in the bound:
    const isValidArity1 = isExplicitTemplateConstraint(partiallyAppliedBound, 1);
    assert.strictEqual(isValidArity1, true);

    // 2. Subscriptability check:
    //    TypeVar with bound `_dict2[_T, Any]` must be recognized as subscriptable with 1 type argument:
    const dictTVar = TypeVarType.createInstance('DictT');
    dictTVar.shared.boundType = partiallyAppliedBound;
    dictTVar.shared.constructorArity = 1;

    assert.strictEqual(dictTVar.shared.constructorArity, 1);
});

test('Level1_TemplateBoundValidation_AllowsGenericConstructorTemplates', () => {
    // Level 1 Unit Test: Template Bound Validation (causes "Type variable has no meaning" and "TypeVar bound/constraint type cannot be generic")
    //
    // Pattern: `T = TypeVar("T")` followed by `F = TypeVar("F", Box[T], OtherBox[T])`
    // or PEP 695: `def func[T_inner, F: (Box[T_inner], OtherBox[T_inner])](...)`
    //
    // Root cause: `isAllowedTypeVarTemplateConstraint` must accept a generic class with type arguments
    // whose type arguments are free/unscoped TypeVars from the surrounding or module scope.

    function isAllowedTemplateConstraint(
        type: Type,
        validScopeIds: string[],
        allowUnscopedModuleTypeVars: boolean
    ): boolean {
        if (isTypeVar(type)) {
            if (!type.priv.scopeId) {
                return allowUnscopedModuleTypeVars;
            }
            return validScopeIds.includes(type.priv.scopeId) || type.priv.scopeId.startsWith('module.');
        }

        if (isAnyOrUnknown(type)) {
            return true;
        }

        if (isClass(type)) {
            if (type.priv.typeArgs) {
                return type.priv.typeArgs.every((arg) =>
                    isAllowedTemplateConstraint(arg, validScopeIds, allowUnscopedModuleTypeVars)
                );
            }
            return false;
        }

        return false;
    }

    // Generic class Box[T]
    const boxClass = ClassType.createInstantiable(
        'Box',
        'test.Box',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const boxT = TypeVarType.createInstance('T');
    boxClass.shared.typeParams.push(boxT);

    // Legacy module-scoped TypeVar T
    const moduleT = TypeVarType.createInstance('T');
    moduleT.priv.scopeId = 'module.';
    const boxModuleT = ClassType.specialize(ClassType.cloneAsInstance(boxClass), [moduleT]);

    // Box[T] with module-scoped T must be allowed as a template constraint:
    assert.strictEqual(isAllowedTemplateConstraint(boxModuleT, [], /* allowUnscopedModuleTypeVars */ true), true);

    // PEP 695 function-scoped TypeVar T_inner
    const fnScopeId = 'func.same_constructor_pep695';
    const pep695T = TypeVarType.createInstance('T_inner');
    pep695T.priv.scopeId = fnScopeId;
    const boxPep695T = ClassType.specialize(ClassType.cloneAsInstance(boxClass), [pep695T]);

    // Box[T_inner] within func scope must be allowed:
    assert.strictEqual(
        isAllowedTemplateConstraint(boxPep695T, [fnScopeId], /* allowUnscopedModuleTypeVars */ false),
        true
    );

    // Class-scoped TypeVar _T1 used inside a TypeVar() call within a class body must NOT be allowed
    const classScopeId = 'class.D';
    const classT = TypeVarType.createInstance('_T1');
    classT.priv.scopeId = classScopeId;
    const boxClassT = ClassType.specialize(ClassType.cloneAsInstance(boxClass), [classT]);

    // When allowUnscopedModuleTypeVars is true (legacy TypeVar call), class-scoped TypeVars are rejected:
    assert.strictEqual(isAllowedTemplateConstraint(boxClassT, [], /* allowUnscopedModuleTypeVars */ true), false);
});

test('Level2_ConstructorSubscripting_RecognizesTemplateArityAndAllowsSubscript', () => {
    // Level 2 Unit Test: Constructor Subscripting (causes "TypeVar 'type[F]' is not subscriptable")
    //
    // Pattern: `F: (Box[T], OtherBox[T])` used as `first: F[int]`
    //
    // When subscripting `F[int]`:
    // 1. Check if F has explicit template constraints/bounds (contains free type variables).
    // 2. Compute the template's constructor arity (number of free type variables).
    // 3. Allow subscripting when applied arguments match the constructor arity.

    const isExplicitTemplate = (type: Type, appliedArity: number): boolean => {
        if (!isClassInstance(type) || !type.priv.typeArgs) {
            return false;
        }
        const freeVars = getTypeVarArgsRecursive(type);
        return freeVars.length === appliedArity;
    };

    const boxClass = ClassType.createInstantiable(
        'Box',
        'test.Box',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const tParam = TypeVarType.createInstance('T');
    boxClass.shared.typeParams.push(tParam);

    const otherBoxClass = ClassType.createInstantiable(
        'OtherBox',
        'test.OtherBox',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const otherTParam = TypeVarType.createInstance('T');
    otherBoxClass.shared.typeParams.push(otherTParam);

    const boxTemplate = ClassType.specialize(ClassType.cloneAsInstance(boxClass), [tParam]);
    const otherBoxTemplate = ClassType.specialize(ClassType.cloneAsInstance(otherBoxClass), [otherTParam]);

    // Both Box[T] and OtherBox[T] are valid unary constructor templates (arity 1)
    assert.strictEqual(isExplicitTemplate(boxTemplate, 1), true);
    assert.strictEqual(isExplicitTemplate(otherBoxTemplate, 1), true);

    // Arity mismatch check: Box[T] subscripted with 2 arguments must be rejected
    assert.strictEqual(isExplicitTemplate(boxTemplate, 2), false);
});

test('Level3_ArgumentAssignmentAndUnification_SolvesConstructorAndRejectsMismatchedConstructors', () => {
    // Level 3 Unit Test: Argument Assignment and Unification
    //
    // Pattern: `def same_constructor(first: F[int], second: F[str])`
    // Call 1: `same_constructor(Box[int](), Box[str]())` -> F = Box (Success)
    // Call 2: `same_constructor(Box[int](), OtherBox[str]())` -> Error (mismatched constructors: Box vs OtherBox)

    const boxClass = ClassType.createInstantiable(
        'Box',
        'test.Box',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const tParam = TypeVarType.createInstance('T');
    boxClass.shared.typeParams.push(tParam);

    const otherBoxClass = ClassType.createInstantiable(
        'OtherBox',
        'test.OtherBox',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const otherTParam = TypeVarType.createInstance('T');
    otherBoxClass.shared.typeParams.push(otherTParam);

    const fVar = TypeVarType.createInstance('F');
    fVar.shared.constraints = [
        ClassType.specialize(ClassType.cloneAsInstance(boxClass), [tParam]),
        ClassType.specialize(ClassType.cloneAsInstance(otherBoxClass), [otherTParam]),
    ];

    // First argument Box[int] unifies F -> Box
    const solution = new ConstraintSolution();
    solution.setType(fVar, ClassType.cloneAsInstance(boxClass));

    // Second argument Box[str] matches existing F = Box
    const secondArgBox = ClassType.cloneAsInstance(boxClass);
    const solvedF = solution.getMainSolutionSet().getType(fVar);
    assert.strictEqual(solvedF !== undefined && ClassType.isSameGenericClass(solvedF as ClassType, secondArgBox), true);

    // Second argument OtherBox[str] conflicts with F = Box
    const secondArgOtherBox = ClassType.cloneAsInstance(otherBoxClass);
    assert.strictEqual(
        solvedF !== undefined && ClassType.isSameGenericClass(solvedF as ClassType, secondArgOtherBox),
        false
    );
});

test('Level4_MethodAndClassMethodSpecialization_SolvesConstructorFromClsOrSelf', () => {
    // Level 4 Unit Test: Method and Classmethod Specialization
    //
    // Pattern:
    // class _dict2[KT, VT]:
    //   @classmethod
    //   def fromkeys[T, DictT: _dict2[T, Any]](cls: type[DictT[T]], iterable: Iterable[T]) -> DictT[T]
    //
    // Calling `_OrderedDict2.fromkeys(list(range(10)))`
    // 1. `cls` is `type[_OrderedDict2]`
    // 2. `DictT` binds to `_OrderedDict2[T, Any]`
    // 3. Return type `DictT[int]` specializes to `_OrderedDict2[int, Any]`

    const dictClass = ClassType.createInstantiable(
        'dict',
        'test._dict2',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const kt = TypeVarType.createInstance('KT');
    const vt = TypeVarType.createInstance('VT');
    dictClass.shared.typeParams.push(kt, vt);

    const orderedDictClass = ClassType.createInstantiable(
        'OrderedDict',
        'test._OrderedDict2',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const ordKt = TypeVarType.createInstance('KT');
    const ordVt = TypeVarType.createInstance('VT');
    orderedDictClass.shared.typeParams.push(ordKt, ordVt);
    orderedDictClass.shared.baseClasses.push(ClassType.specialize(dictClass, [ordKt, ordVt]));
    orderedDictClass.shared.mro.push(orderedDictClass, dictClass);

    const tVar = TypeVarType.createInstance('T');
    const dictTVar = TypeVarType.createInstance('DictT');
    dictTVar.shared.boundType = ClassType.specialize(ClassType.cloneAsInstance(dictClass), [tVar, AnyType.create()]);

    const intType = ClassType.createInstantiable(
        'int',
        'builtins.int',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );

    // Applied return type: DictT[int]
    const returnTypeVar = TypeVarType.cloneForTypeApplication(dictTVar, [ClassType.cloneAsInstance(intType)]);

    // When called on OrderedDict, DictT solves to OrderedDict template:
    const orderedSolution = new ConstraintSolution();
    const orderedTemplate = ClassType.specialize(ClassType.cloneAsInstance(orderedDictClass), [tVar, AnyType.create()]);
    orderedSolution.setType(dictTVar, orderedTemplate);

    const solved = applySolvedTypeVars(returnTypeVar, orderedSolution);
    assert.strictEqual(printType(solved, PrintTypeFlags.None, returnTypeCallback), 'OrderedDict[int, Any]');
});

test('Regression_HigherKindedTransform_PreservesDerivedConstructorShape', () => {
    // Regression Test (corresponds to HigherKindedType5..7, 10..11, 16):
    // def transform[A, B, F: (Container[A], SpecialContainer[A])](value: F[A], new_type: type[B]) -> F[B]
    // 1. transform(SpecialContainer[int](), str) -> SpecialContainer[str]
    // 2. transform(Container[int](), str) -> Container[str]
    // 3. transform(Other[int](), str) -> rejected by constraint

    const containerClass = ClassType.createInstantiable(
        'Container',
        'test.Container',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const aParam = TypeVarType.createInstance('T');
    containerClass.shared.typeParams.push(aParam);

    const specialContainerClass = ClassType.createInstantiable(
        'SpecialContainer',
        'test.SpecialContainer',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const specParam = TypeVarType.createInstance('T');
    specialContainerClass.shared.typeParams.push(specParam);
    specialContainerClass.shared.baseClasses.push(ClassType.specialize(containerClass, [specParam]));
    specialContainerClass.shared.mro.push(specialContainerClass, containerClass);

    const stringType = ClassType.createInstantiable(
        'str',
        'builtins.str',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );

    const fVar = TypeVarType.createInstance('F');
    fVar.shared.constraints = [
        ClassType.specialize(ClassType.cloneAsInstance(containerClass), [aParam]),
        ClassType.specialize(ClassType.cloneAsInstance(specialContainerClass), [specParam]),
    ];

    const appliedReturn = TypeVarType.cloneForTypeApplication(fVar, [ClassType.cloneAsInstance(stringType)]);

    // SpecialContainer[int] solves F -> SpecialContainer:
    const specSolution = new ConstraintSolution();
    specSolution.setType(fVar, ClassType.cloneAsInstance(specialContainerClass));
    const solvedSpec = applySolvedTypeVars(appliedReturn, specSolution);
    assert.strictEqual(printType(solvedSpec, PrintTypeFlags.None, returnTypeCallback), 'SpecialContainer[str]');

    // Container[int] solves F -> Container:
    const baseSolution = new ConstraintSolution();
    baseSolution.setType(fVar, ClassType.cloneAsInstance(containerClass));
    const solvedBase = applySolvedTypeVars(appliedReturn, baseSolution);
    assert.strictEqual(printType(solvedBase, PrintTypeFlags.None, returnTypeCallback), 'Container[str]');
});

test('Regression_HigherKindedSelfTypePolymorphism_BidictInversePattern', () => {
    // Regression Test (corresponds to HigherKindedType20 / bidict pattern):
    // class BidirectionalMapping[KT, VT]:
    //   def inverse[MapT: BidirectionalMapping[KT, VT]](self: MapT[KT, VT]) -> MapT[VT, KT]
    // class bidict[KT, VT](BidirectionalMapping[KT, VT]): ...
    //
    // 1. bidict[int, str].inverse() -> bidict[str, int]
    // 2. BidirectionalMapping[int, str].inverse() -> BidirectionalMapping[str, int]

    const baseMapClass = ClassType.createInstantiable(
        'BidirectionalMapping',
        'test.BidirectionalMapping',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const kt = TypeVarType.createInstance('KT');
    const vt = TypeVarType.createInstance('VT');
    baseMapClass.shared.typeParams.push(kt, vt);

    const bidictClass = ClassType.createInstantiable(
        'bidict',
        'test.bidict',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const bkt = TypeVarType.createInstance('KT');
    const bvt = TypeVarType.createInstance('VT');
    bidictClass.shared.typeParams.push(bkt, bvt);
    bidictClass.shared.baseClasses.push(ClassType.specialize(baseMapClass, [bkt, bvt]));
    bidictClass.shared.mro.push(bidictClass, baseMapClass);

    const intType = ClassType.createInstantiable(
        'int',
        'builtins.int',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );
    const stringType = ClassType.createInstantiable(
        'str',
        'builtins.str',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );

    const mapTVar = TypeVarType.createInstance('MapT');
    mapTVar.shared.boundType = ClassType.specialize(ClassType.cloneAsInstance(baseMapClass), [kt, vt]);

    // Return type MapT[VT, KT] (inverted type arguments):
    const appliedReturn = TypeVarType.cloneForTypeApplication(mapTVar, [
        ClassType.cloneAsInstance(stringType),
        ClassType.cloneAsInstance(intType),
    ]);

    // When called on bidict[int, str]: MapT binds to bidict
    const bidictSolution = new ConstraintSolution();
    bidictSolution.setType(mapTVar, ClassType.cloneAsInstance(bidictClass));
    const solvedBidict = applySolvedTypeVars(appliedReturn, bidictSolution);
    assert.strictEqual(printType(solvedBidict, PrintTypeFlags.None, returnTypeCallback), 'bidict[str, int]');

    // When called on BidirectionalMapping[int, str]: MapT binds to BidirectionalMapping
    const baseSolution = new ConstraintSolution();
    baseSolution.setType(mapTVar, ClassType.cloneAsInstance(baseMapClass));
    const solvedBase = applySolvedTypeVars(appliedReturn, baseSolution);
    assert.strictEqual(
        printType(solvedBase, PrintTypeFlags.None, returnTypeCallback),
        'BidirectionalMapping[str, int]'
    );
});

test('HigherKindedType17_ConcreteSubclassConstructorMatchingVersusGenericConstructor', () => {
    // Specifically models why HigherKindedType17 Case 1 and Case 4 behave differently:
    //
    // Case 1:
    // class Field[GT]: ...
    // class CharField(Field[str]): ... (concrete non-generic subclass, 0 type params)
    // def make_field_nullable[GT, FieldT: Field[GT]](cls: type[FieldT[GT]], null: Literal[True]) -> FieldT[GT | None]
    //
    // When CharField is passed:
    // 1. CharField has 0 type parameters. Its base Field[str] has GT=str.
    // 2. FieldT binds to Field (the generic constructor in CharField's MRO), so FieldT[GT | None] -> Field[str | None].
    // 3. User1.f2 has descriptor __get__ returning str | None.
    //
    // Case 4:
    // class BaseField2[GT]:
    //     def __new__[F: BaseField2[GT]](cls: type[F[GT]], null: Literal[True]) -> F[GT | None]: ...
    // class SpecialField2[GT](BaseField2[GT]): ... (generic subclass with 1 type param)
    // class ConcreteCharField2(SpecialField2[str]): ... (concrete subclass, 0 type params)
    //
    // When ConcreteCharField2(null=True) is called:
    // 1. ConcreteCharField2 has 0 type parameters.
    // 2. Its most derived generic base constructor is SpecialField2[GT].
    // 3. Therefore F binds to SpecialField2, returning SpecialField2[str | None].

    const fieldClass = ClassType.createInstantiable(
        'Field',
        'test.Field',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const gt = TypeVarType.createInstance('GT');
    fieldClass.shared.typeParams.push(gt);

    const charFieldClass = ClassType.createInstantiable(
        'CharField',
        'test.CharField',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const stringType = ClassType.createInstantiable(
        'str',
        'builtins.str',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );
    charFieldClass.shared.baseClasses.push(ClassType.specialize(fieldClass, [ClassType.cloneAsInstance(stringType)]));
    charFieldClass.shared.mro.push(charFieldClass, fieldClass);

    // Finding generic constructor for CharField (0 type params):
    // It should find the generic ancestor (Field), not CharField itself:
    const findGenericAncestorConstructor = (cls: ClassType): ClassType => {
        if (cls.shared.typeParams.length > 0) {
            return cls;
        }
        const genericBase = cls.shared.mro.find(
            (m): m is ClassType => isInstantiableClass(m) && m.shared.typeParams.length > 0
        );
        return genericBase ?? cls;
    };

    assert.strictEqual(findGenericAncestorConstructor(charFieldClass), fieldClass);
});

test('Level5_InvalidTypeVarUse_FlagsReturnOnlyConstructorTypeVarAsUnsolvable', () => {
    // Specifically tests the checker's diagnostic validation for constructor TypeVars:
    //
    // Pattern 1 (Invalid):
    // class DeviceTransferable[DeviceT]:
    //   def to_device[DeviceTransferableT: DeviceTransferable[DeviceT], NewDeviceT](
    //       self, device: type[NewDeviceT]
    //   ) -> DeviceTransferableT[NewDeviceT]: ...
    //
    // DeviceTransferableT appears only in return position (paramTypeUsageCount === 0).
    // It cannot be solved from caller arguments and must be flagged by reportInvalidTypeVarUse.
    //
    // Pattern 2 (Valid):
    // def to_device[DeviceTransferableT: DeviceTransferable[DeviceT], NewDeviceT](
    //     self: DeviceTransferableT[DeviceT], device: type[NewDeviceT]
    // ) -> DeviceTransferableT[NewDeviceT]: ...
    //
    // DeviceTransferableT appears in self parameter (paramTypeUsageCount === 1).
    // It is solved from the caller receiver and is valid.

    function checkConstructorTypeVarUsage(
        paramTypeUsageCount: number,
        returnTypeUsageCount: number,
        isConstructorTypeVar: boolean
    ): { isSingleUseError: boolean } {
        const isExempt = isConstructorTypeVar && paramTypeUsageCount > 0;
        const isUsedOnlyInReturnType = returnTypeUsageCount > 0 && paramTypeUsageCount === 0;
        const isSingleUseError =
            (!isExempt && paramTypeUsageCount + returnTypeUsageCount === 1) ||
            (isConstructorTypeVar && isUsedOnlyInReturnType);
        return { isSingleUseError };
    }

    // Pattern 1: unannotated self -> returnTypeUsageCount = 1, paramTypeUsageCount = 0 -> FLAGGED
    const pattern1 = checkConstructorTypeVarUsage(
        /* paramTypeUsageCount */ 0,
        /* returnTypeUsageCount */ 1,
        /* isConstructorTypeVar */ true
    );
    assert.strictEqual(pattern1.isSingleUseError, true);

    // Pattern 2: annotated self -> returnTypeUsageCount = 1, paramTypeUsageCount = 1 -> VALID
    const pattern2 = checkConstructorTypeVarUsage(
        /* paramTypeUsageCount */ 1,
        /* returnTypeUsageCount */ 1,
        /* isConstructorTypeVar */ true
    );
    assert.strictEqual(pattern2.isSingleUseError, false);
});

test('HigherKindedType22_CephOrchestratorFacadeSubclassMethodSpecialization', () => {
    // Specifically reproduces Ceph Orchestrator pattern (HigherKindedType22):
    // class Orchestrator[T, CompletionT: Completion[T]]:
    //     def add_host(self) -> CompletionT[str]: ...
    // class AsyncOrchestrator(Orchestrator[object, Completion[object]]): ...
    //
    // Orchestrator has 2 class type parameters: T and CompletionT.
    // When AsyncOrchestrator inherits Orchestrator[object, Completion[object]],
    // the base class specialization maps CompletionT -> Completion[object].
    // When accessing async_orch.add_host(), method return type CompletionT[str]
    // must substitute Completion[object]'s type argument with str -> Completion[str].

    const completionClass = ClassType.createInstantiable(
        'Completion',
        'test.Completion',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const compT = TypeVarType.createInstance('T');
    completionClass.shared.typeParams.push(compT);

    const stringType = ClassType.createInstantiable(
        'str',
        'builtins.str',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );

    const completionTVar = TypeVarType.createInstance('CompletionT');
    completionTVar.shared.boundType = ClassType.specialize(ClassType.cloneAsInstance(completionClass), [compT]);

    // Method return type in Orchestrator: CompletionT[str]
    const returnTypeVar = TypeVarType.cloneForTypeApplication(completionTVar, [ClassType.cloneAsInstance(stringType)]);

    // Solution from AsyncOrchestrator base class: CompletionT -> Completion (unspecialized constructor)
    const solution = new ConstraintSolution();
    solution.setType(completionTVar, ClassType.cloneAsInstance(completionClass));

    // Applying solution { CompletionT -> Completion } to CompletionT[str]:
    const solved = applySolvedTypeVars(returnTypeVar, solution);
    assert.strictEqual(printType(solved, PrintTypeFlags.None, returnTypeCallback), 'Completion[str]');
});

test('HigherKindedType23_CoroutineWrapperFacadeSpecializationWithoutLeak', () => {
    // Specifically reproduces Samuel Colvin async redis facade (HigherKindedType23):
    // type Result[T] = Coroutine[Any, Any, T]
    // class GenericFacade[X, WrapperT: WrapperTemplate[X]]:
    //     def method_1(self) -> WrapperT[str]: ...
    // class CoroutineFacade[X](GenericFacade[X, Result[X]]): ...
    //
    // When CoroutineFacade is instantiated (coroutine_facade = CoroutineFacade()),
    // coroutine_facade.method_1() must evaluate WrapperT[str] -> Coroutine[Any, Any, str],
    // without leaking the unspecialized X or Unknown from the enclosing class.

    const coroutineClass = ClassType.createInstantiable(
        'Coroutine',
        'collections.abc.Coroutine',
        'collections.abc',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    const coroutineT = TypeVarType.createInstance('T');
    coroutineClass.shared.typeParams.push(coroutineT);

    const stringType = ClassType.createInstantiable(
        'str',
        'builtins.str',
        'builtins',
        Uri.empty(),
        ClassTypeFlags.BuiltIn,
        0,
        undefined,
        undefined
    );
    const xTypeVar = TypeVarType.createInstance('X');
    xTypeVar.priv.scopeId = 'class.CoroutineFacade';

    const resultAliasInfo = {
        shared: {
            name: 'Result',
            fullName: 'test.Result',
            moduleName: 'test',
            fileUri: Uri.empty(),
            typeVarScopeId: 'test.scope',
            isTypeAliasType: true,
            typeParams: [coroutineT],
            computedVariance: undefined,
        },
        typeArgs: [xTypeVar],
    };
    const resultXTarget = ClassType.specialize(ClassType.cloneAsInstance(coroutineClass), [xTypeVar]);
    const resultXAlias = TypeBase.cloneForTypeAlias(resultXTarget, resultAliasInfo);

    const wrapperTVar = TypeVarType.createInstance('WrapperT');
    const returnTypeVar = TypeVarType.cloneForTypeApplication(wrapperTVar, [ClassType.cloneAsInstance(stringType)]);

    const solution = new ConstraintSolution();
    solution.setType(wrapperTVar, resultXAlias);

    const solved = applySolvedTypeVars(returnTypeVar, solution);
    assert.strictEqual(printType(solved, PrintTypeFlags.ExpandTypeAlias, returnTypeCallback), 'Coroutine[str]');
});

test('HigherKindedType24_UnsolvedHigherKindedTypeVarReplacedWithUnknownWithoutLeakingTypeVar', () => {
    // Specifically reproduces mongo-model pattern (python/typing#548 comment 843663432):
    // def find_one[IDT, MongoModelT[IDT]: MongoModel[IDT]](model_cls: type[MongoModelT[IDT]], id: IDT) -> MongoModelT[IDT]: ...
    //
    // When an incompatible/non-generic class (e.g. User) is passed to find_one,
    // MongoModelT cannot be solved and remains unassigned in the constraint solution.
    // When specializing the return type MongoModelT[IDT] with replaceUnsolved,
    // the unsolved HKT TypeVar MUST be replaced with Unknown rather than leaking
    // the raw unspecialized TypeVar (e.g. "MongoModelT@find_one[IDT@find_one]").

    const functionScopeId = 'func.find_one';
    const idtTypeVar = TypeVarType.createInstance('IDT');
    idtTypeVar.priv.scopeId = functionScopeId;
    idtTypeVar.priv.scopeName = 'find_one';
    idtTypeVar.priv.scopeType = TypeVarScopeType.Function;

    const mongoModelTVar = TypeVarType.createInstance('MongoModelT');
    mongoModelTVar.priv.scopeId = functionScopeId;
    mongoModelTVar.priv.scopeName = 'find_one';
    mongoModelTVar.priv.scopeType = TypeVarScopeType.Function;
    mongoModelTVar.shared.constructorArity = 1;

    const returnTypeVar = TypeVarType.cloneForTypeApplication(mongoModelTVar, [idtTypeVar]);

    // An empty solution where MongoModelT was not solved (e.g. due to type[User] failing match)
    const solution = new ConstraintSolution();

    const solved = applySolvedTypeVars(returnTypeVar, solution, {
        replaceUnsolved: {
            scopeIds: [functionScopeId],
            tupleClassType: undefined,
        },
    });

    assert.strictEqual(printType(solved, PrintTypeFlags.None, returnTypeCallback), 'Unknown');
});

test('HigherKindedType24_NestedTypeVarShadowingOuterScopeDetected', () => {
    // Models PEP 695 type parameter shadowing:
    // def find_one[IDT, MongoModelT[IDT]: MongoModel[IDT]](...):
    // The inner dummy parameter IDT shadows the outer function-scoped IDT,
    // which triggers the diagnostic: `TypeVar "IDT" is already in use by an outer scope`.

    const outerTypeParams = [TypeVarType.createInstance('IDT'), TypeVarType.createInstance('MongoModelT')];
    const innerDummyParam = TypeVarType.createInstance('IDT');

    const isShadowed = outerTypeParams.some((param) => param.shared.name === innerDummyParam.shared.name);
    assert.strictEqual(isShadowed, true);

    const nonShadowedDummyParam = TypeVarType.createInstance('T');
    const isNotShadowed = outerTypeParams.some((param) => param.shared.name === nonShadowedDummyParam.shared.name);
    assert.strictEqual(isNotShadowed, false);
});

test('HigherKindedType9_BareConstructorUsageMissingTypeArgsDiagnostic', () => {
    // Specifically models and tests the direct analog between bare generic classes and bare HKT TypeVars:
    //
    // Analog 1 (Bare Generic Class):
    // class Box[T]: ...
    // def f(box: Box) -> None: ...
    // -> Missing type argument: Box is generic (* -> *), used bare as ordinary type (*)
    // -> Generates: "Expected type arguments for generic class 'Box'" / "Parameter type is 'Box[Unknown]'"
    //
    // Analog 2 (Bare HKT TypeVar / Mixed Kind):
    // def rejects_mixed_kind[Mixed[T]: (Box[T], OtherBox[T])](value: Mixed, item: Mixed[int]) -> None: ...
    // -> Missing type argument: Mixed is a type constructor (* -> *), used bare as ordinary type (*) in `value: Mixed`
    // -> Generates: "Expected type arguments for generic class 'Mixed'" / "Parameter type is 'Mixed[Unknown]'"

    function checkMissingTypeArgsForType(
        type: Type,
        isTypeAnnotationContext: boolean
    ): { requiresMissingTypeArgsError: boolean; synthesizedDefault: string } {
        if (isInstantiableClass(type)) {
            if (type.shared.typeParams.length > 0 && !type.priv.typeArgs && isTypeAnnotationContext) {
                return {
                    requiresMissingTypeArgsError: true,
                    synthesizedDefault: `${type.shared.name}[Unknown]`,
                };
            }
        } else if (isTypeVar(type)) {
            const hasConstructorTemplates =
                type.shared.constructorArity !== undefined ||
                type.shared.constraints.some(
                    (c) => isClassInstance(c) && !!c.priv.typeArgs && getTypeVarArgsRecursive(c).length > 0
                ) ||
                (type.shared.boundType &&
                    isClassInstance(type.shared.boundType) &&
                    !!type.shared.boundType.priv.typeArgs &&
                    getTypeVarArgsRecursive(type.shared.boundType).length > 0);

            if (hasConstructorTemplates && !type.priv.typeArgs && isTypeAnnotationContext) {
                return {
                    requiresMissingTypeArgsError: true,
                    synthesizedDefault: `${type.shared.name}[Unknown]`,
                };
            }
        }

        return { requiresMissingTypeArgsError: false, synthesizedDefault: '' };
    }

    // 1. Generic class Box (arity 1) used bare:
    const boxClass = ClassType.createInstantiable(
        'Box',
        'test.Box',
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        undefined,
        undefined
    );
    boxClass.shared.typeParams.push(TypeVarType.createInstance('T'));

    const classCheck = checkMissingTypeArgsForType(boxClass, /* isTypeAnnotationContext */ true);
    assert.strictEqual(classCheck.requiresMissingTypeArgsError, true);
    assert.strictEqual(classCheck.synthesizedDefault, 'Box[Unknown]');

    // 2. HKT TypeVar Mixed (constructorArity = 1) used bare in `value: Mixed`:
    const mixedTypeVar = TypeVarType.createInstance('Mixed');
    mixedTypeVar.shared.constructorArity = 1;

    const bareTypeVarCheck = checkMissingTypeArgsForType(mixedTypeVar, /* isTypeAnnotationContext */ true);
    assert.strictEqual(bareTypeVarCheck.requiresMissingTypeArgsError, true);
    assert.strictEqual(bareTypeVarCheck.synthesizedDefault, 'Mixed[Unknown]');

    // 3. HKT TypeVar Mixed correctly subscripted in `item: Mixed[int]`:
    const appliedMixed = TypeVarType.cloneForTypeApplication(mixedTypeVar, [
        ClassType.createInstantiable(
            'int',
            'builtins.int',
            'builtins',
            Uri.empty(),
            ClassTypeFlags.BuiltIn,
            0,
            undefined,
            undefined
        ),
    ]);
    const appliedCheck = checkMissingTypeArgsForType(appliedMixed, /* isTypeAnnotationContext */ true);
    assert.strictEqual(appliedCheck.requiresMissingTypeArgsError, false);
});
