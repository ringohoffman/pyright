/// <reference path="typings/fourslash.d.ts" />

// @filename: pyrightconfig.json
//// {
////   "pythonVersion": "3.16"
//// }

// @filename: test.py
//// class Container[T]: ...
////
//// # Renaming the inner parameter touches only the constructor parameter's
//// # own declaration and bound.
//// def func1[F[[|[|/*marker*/Inner|]|]]: Container[[|Inner|]]](x: F[int]) -> F[str]: ...
////
//// # A same-named inner parameter on a different constructor is unrelated.
//// def func2[G[Inner]: Container[Inner]](x: G[int]) -> None: ...

{
    const ranges = helper.getRanges().filter((r) => !r.marker);

    helper.verifyRename({
        marker: {
            newName: 'Elem',
            changes: ranges.map((r) => {
                return { filePath: r.fileName, range: helper.convertPositionRange(r), replacementText: 'Elem' };
            }),
        },
    });
}
