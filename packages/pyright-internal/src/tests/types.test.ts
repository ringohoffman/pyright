/*
 * types.test.ts
 * Copyright (c) Microsoft Corporation.
 * Licensed under the MIT license.
 *
 * Unit tests for the type model and related utilities.
 */

import * as assert from 'assert';

import { ConstraintSolution } from '../analyzer/constraintSolution';
import { applyTypeNarrowingCallback } from '../analyzer/typeGuards';
import { printType, PrintTypeFlags } from '../analyzer/typePrinter';
import { applySolvedTypeVars, validateTypeVarDefault } from '../analyzer/typeUtils';
import {
    ClassType,
    ClassTypeFlags,
    combineTypes,
    exceedsInferredTupleLiteralProduct,
    getInferredTupleLiteralBase,
    isTypeSame,
    retainInferredTupleLiterals,
    Type,
    TypeBase,
    TypeVarScopeType,
    TypeVarType,
    UnknownType,
} from '../analyzer/types';
import { Uri } from '../common/uri/uri';

function returnTypeCallback(type: any) {
    return type.shared.declaredReturnType ?? UnknownType.create(/* isEllipsis */ true);
}

function createClass(name: string, typeParamNames: string[] = []): ClassType {
    const classType = ClassType.createInstantiable(
        name,
        `test.${name}`,
        'test',
        Uri.empty(),
        ClassTypeFlags.None,
        0,
        /* declaredMetaclass */ undefined,
        /* effectiveMetaclass */ undefined
    );
    classType.shared.typeParams = typeParamNames.map((paramName) => TypeVarType.createInstance(paramName));
    return classType;
}

function instance(classType: ClassType, typeArgs?: Type[]): ClassType {
    const result = ClassType.cloneAsInstance(classType);
    return typeArgs ? ClassType.specialize(result, typeArgs) : result;
}

function print(type: Type): string {
    return printType(type, PrintTypeFlags.None, returnTypeCallback);
}

// --- Higher-kinded type constructor TypeVars ---------------------------------

test('TypeVarIsConstructor', () => {
    const plain = TypeVarType.createInstance('T');
    assert.strictEqual(TypeVarType.isConstructor(plain), false);

    const constructor = TypeVarType.createInstance('F');
    constructor.shared.typeParams = [TypeVarType.createInstance('T')];
    assert.strictEqual(TypeVarType.isConstructor(constructor), true);
});

test('IsTypeSameDistinguishesAppliedTypeArgs', () => {
    const intType = instance(createClass('int'));
    const strType = instance(createClass('str'));

    const f = TypeVarType.createInstance('F');
    f.shared.typeParams = [TypeVarType.createInstance('T')];

    const fInt = TypeVarType.cloneForTypeApplication(f, [intType]);
    const fIntAgain = TypeVarType.cloneForTypeApplication(f, [intType]);
    const fStr = TypeVarType.cloneForTypeApplication(f, [strType]);

    assert.strictEqual(isTypeSame(fInt, fIntAgain), true);
    assert.strictEqual(isTypeSame(fInt, fStr), false);
    assert.strictEqual(isTypeSame(f, fInt), false);
});

test('PrintTypeShowsAppliedTypeArgs', () => {
    const f = TypeVarType.createInstance('F');
    f.shared.typeParams = [TypeVarType.createInstance('T')];
    const fInt = TypeVarType.cloneForTypeApplication(f, [instance(createClass('int'))]);

    assert.strictEqual(print(fInt), 'F[int]');
});

test('ApplySolvedTypeVarsAppliesConstructorSolutionToTypeArgs', () => {
    // Solving F := Array and then applying F[str] yields Array[str].
    const arrayClass = createClass('Array', ['S']);
    const strType = instance(createClass('str'));

    const f = TypeVarType.createInstance('F');
    f.shared.typeParams = [TypeVarType.createInstance('T')];
    const fStr = TypeVarType.cloneForTypeApplication(f, [strType]);

    const solution = new ConstraintSolution();
    solution.setType(f, instance(arrayClass));

    assert.strictEqual(print(applySolvedTypeVars(fStr, solution)), 'Array[str]');
});

test('ApplySolvedTypeVarsSpecializesConstraintTemplate', () => {
    // ArrayT: Array[Scalar[D]]; solving ArrayT := Array[Scalar[D]] and
    // applying ArrayT[str] substitutes D := str inside the template.
    const scalarClass = createClass('Scalar', ['D']);
    const arrayClass = createClass('Array', ['S']);
    const strType = instance(createClass('str'));

    const d = scalarClass.shared.typeParams[0];
    const template = instance(arrayClass, [instance(scalarClass, [d])]);

    const arrayT = TypeVarType.createInstance('ArrayT');
    arrayT.shared.constraints = [template];
    arrayT.shared.typeParams = [d];
    const applied = TypeVarType.cloneForTypeApplication(arrayT, [strType]);

    const solution = new ConstraintSolution();
    solution.setType(arrayT, template);

    assert.strictEqual(print(applySolvedTypeVars(applied, solution)), 'Array[Scalar[str]]');
});

test('ApplySolvedTypeVarsReplacesUnsolvedAppliedConstructorWithUnknown', () => {
    // An unsolved F[T] in a return type must become Unknown rather than leak
    // the raw TypeVar when replaceUnsolved is requested.
    const scopeId = 'func.find_one';
    const idt = TypeVarType.createInstance('IDT');
    idt.priv.scopeId = scopeId;
    idt.priv.scopeName = 'find_one';
    idt.priv.scopeType = TypeVarScopeType.Function;

    const modelT = TypeVarType.createInstance('ModelT');
    modelT.priv.scopeId = scopeId;
    modelT.priv.scopeName = 'find_one';
    modelT.priv.scopeType = TypeVarScopeType.Function;
    modelT.shared.typeParams = [idt];

    const applied = TypeVarType.cloneForTypeApplication(modelT, [idt]);
    const solved = applySolvedTypeVars(applied, new ConstraintSolution(), {
        replaceUnsolved: { scopeIds: [scopeId], tupleClassType: undefined },
    });

    assert.strictEqual(print(solved), 'Unknown');
});

test('ValidateTypeVarDefaultTreatsInnerParamsAsLive', () => {
    // class A[WrapperT[T] = Identity[T]]: the inner parameter T is in scope
    // for WrapperT's default only when it is supplied as a live parameter.
    const t = TypeVarType.createInstance('T');
    const identityAlias = TypeBase.cloneForTypeAlias(t, {
        shared: {
            name: 'Identity',
            fullName: 'test.Identity',
            moduleName: 'test',
            fileUri: Uri.empty(),
            typeVarScopeId: 'test_alias_scope',
            isTypeAliasType: true,
            typeParams: [t],
            computedVariance: undefined,
            unspecializedType: t,
        },
        typeArgs: [t],
    });

    const wrapperT = TypeVarType.createInstance('WrapperT');
    wrapperT.shared.typeParams = [t];
    wrapperT.shared.isDefaultExplicit = true;
    wrapperT.shared.defaultType = identityAlias;

    const withoutInner = new Set<string>();
    validateTypeVarDefault(wrapperT, [], withoutInner);
    assert.strictEqual(withoutInner.has('T'), true);

    const withInner = new Set<string>();
    validateTypeVarDefault(wrapperT, [t], withInner);
    assert.strictEqual(withInner.size, 0);
});

// --- Upstream ---------------------------------------------------------------

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

test('InferredTupleLiteralGuardViews', () => {
    const base = ClassType.cloneAsInstance(
        ClassType.createInstantiable(
            'int',
            'builtins.int',
            'builtins',
            Uri.empty(),
            ClassTypeFlags.BuiltIn,
            0,
            /* declaredMetaclass */ undefined,
            /* effectiveMetaclass */ undefined
        )
    );
    const literal = ClassType.cloneWithLiteral(base, 1);
    const retained = retainInferredTupleLiterals(literal, base);
    let calls = 0;

    const independent = applyTypeNarrowingCallback((type) => {
        calls++;
        return { type: type === base ? literal : type, isIncomplete: type === base };
    }, retained);
    assert.ok(independent);
    assert.strictEqual(calls, 2);
    assert.strictEqual(independent.type, literal);
    assert.strictEqual(independent.type.props?.inferredTupleLiteral, undefined);
    assert.strictEqual(independent.isIncomplete, true);

    const guardedBase = combineTypes([literal, ClassType.cloneWithLiteral(base, 2)]);
    calls = 0;
    const membership = applyTypeNarrowingCallback((type) => {
        calls++;
        return { type: type === base ? guardedBase : type, isIncomplete: false };
    }, retained);
    assert.ok(membership);
    assert.strictEqual(calls, 2);
    assert.ok(isTypeSame(membership.type, literal));
    assert.strictEqual(getInferredTupleLiteralBase(membership.type), guardedBase);

    const inferred = applyTypeNarrowingCallback(() => ({ type: retained, isIncomplete: false }), retained);
    assert.ok(inferred);
    assert.strictEqual(getInferredTupleLiteralBase(inferred.type), base);
    assert.strictEqual(getInferredTupleLiteralBase(retained), base);

    calls = 0;
    applyTypeNarrowingCallback((type) => {
        calls++;
        return { type, isIncomplete: false };
    }, base);
    assert.strictEqual(calls, 1);
});

test('InferredTupleLiteralProductBudget', () => {
    const base = ClassType.cloneAsInstance(
        ClassType.createInstantiable(
            'int',
            'builtins.int',
            'builtins',
            Uri.empty(),
            ClassTypeFlags.BuiltIn,
            0,
            /* declaredMetaclass */ undefined,
            /* effectiveMetaclass */ undefined
        )
    );
    const choices = Array.from({ length: 9 }, (_, index) => ClassType.cloneWithLiteral(base, index));
    const eight = combineTypes(choices.slice(0, 8));
    const retained = retainInferredTupleLiterals(eight, base);
    assert.strictEqual(retained.props?.inferredTupleLiteral?.alternatives, 8);
    assert.strictEqual(exceedsInferredTupleLiteralProduct(retained, eight), false);
    assert.strictEqual(exceedsInferredTupleLiteralProduct(retained, combineTypes(choices)), true);

    const opaque = TypeVarType.createInstance('T');
    opaque.shared.boundType = combineTypes(choices);
    assert.strictEqual(exceedsInferredTupleLiteralProduct(retained, opaque), true);
    assert.strictEqual(exceedsInferredTupleLiteralProduct(opaque, retained), true);
    assert.strictEqual(exceedsInferredTupleLiteralProduct(retained, combineTypes([base, opaque])), true);
    assert.strictEqual(exceedsInferredTupleLiteralProduct(base, opaque), false);
});
