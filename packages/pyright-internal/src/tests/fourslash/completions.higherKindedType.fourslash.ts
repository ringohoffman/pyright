/// <reference path="typings/fourslash.d.ts" />

// @filename: pyrightconfig.json
//// {
////   "pythonVersion": "3.16"
//// }

// @filename: test.py
//// class Container[T]: ...
////
//// # The inner parameter is visible within the bound of its own constructor
//// # parameter, and the constructor parameter is visible in the signature.
//// def func1[F[Inner]: Container[[|In/*bound*/|]]](x: [|/*param*/|]F[int]) -> None: ...
////
//// # The inner parameter is NOT visible in the signature or body.
//// def func2[F[Inner]](x: F[int]) -> None:
////     y: [|Inn/*body*/|]

{
    helper.openFiles(helper.getMarkers().map((m) => m.fileName));

    // @ts-ignore
    await helper.verifyCompletion('included', 'markdown', {
        bound: {
            completions: [{ label: 'Inner', kind: Consts.CompletionItemKind.TypeParameter }],
        },
        param: {
            completions: [{ label: 'F', kind: Consts.CompletionItemKind.TypeParameter }],
        },
    });

    // @ts-ignore
    await helper.verifyCompletion('excluded', 'markdown', {
        body: {
            completions: [{ label: 'Inner', kind: Consts.CompletionItemKind.TypeParameter }],
        },
    });
}
