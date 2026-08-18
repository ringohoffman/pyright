# Higher-Kinded Type Development

This directory contains focused prototypes for higher-kinded TypeVars. The active example mirrors the relevant `pyarrow` API while keeping import discovery and runtime dependencies local.

See `ROADMAP.md` for the complete implementation status, red-test inventory, design decisions, and ordered handoff plan.

## Initial setup

From the repository root:

```bash
npm install
npm run build:cli:dev
npm --prefix packages/pyright-typeserver run webpack
```

The first command installs dependencies for every package. The second builds the standalone Pyright CLI. The third builds the Type Server Protocol (TSP) bundle used by Pylance.

The workspace selects `.venv/bin/python`. The prototype itself does not require the real `pyarrow` package because `pyarrow-cast/pyarrow/` provides the narrow API surface under the real module names.

## Test-driven implementation loop

The staged tests live in `packages/pyright-internal/src/tests/samples/higherKindedType*.py` and are registered in `typeEvaluator7.test.ts`.

Run all HKT checkpoints:

```bash
cd packages/pyright-internal
npx jest typeEvaluator7.test -t HigherKindedType --forceExit --runInBand
```

Run one checkpoint while implementing it:

```bash
npx jest typeEvaluator7.test -t HigherKindedType3 --forceExit --runInBand
```

Run the neighboring regression suite and printer tests:

```bash
npx jest typeEvaluator7.test typePrinter.test --forceExit --runInBand
```

Compile the engine after TypeScript changes:

```bash
npm run build
```

## Check the canonical prototype

After building `pyright-internal`, run:

```bash
cd ../..
node packages/pyright-internal/debug.js \
  --typeshedpath packages/pyright-internal/typeshed-fallback \
  --project hkt-prototypes/pyarrow-cast/pyrightconfig.json
```

The overload and HKT results should agree:

```text
Array[Scalar[StringType]]
ChunkedArray[Scalar[StringType]]
```

## Use the modified engine in the editor

The verified workflow uses the open-source Pyright extension in an Extension Development Host:

1. Select **Pyright HKT extension (watch)** in Run and Debug.
2. Press `F5`.
3. The development window opens `hkt-prototypes/pyarrow-cast` with conflicting analyzers and bundled Copilot disabled. Bundled Python language support remains enabled for grammar and syntax highlighting.
4. Reload the development window after a rebuild.

This route keeps evaluation, type printing, hover generation, and diagnostics on the same modified Pyright codebase.
The prototype-local `.vscode/settings.json` sets `python.languageServer` to `None` so the Python extension does not fall back to Jedi when Pylance is disabled. The development Pyright extension is the sole language server in that window.
The launch target uses `${execPath}` as the Extension Host runtime. It disables Pylance, published Pyright, and bundled Copilot individually; it must not use `--disable-extensions`, because that also disables bundled Python grammar support. The debugger skips bundled extension and Node-internal sources so unrelated exceptions cannot stop Pyright debugging.

## Experimental active-Pylance bridge

Pylance can delegate type evaluation to this repository's `pyright-typeserver` over TSP. The workspace settings configure:

```json
"python.analysis.enableExternalTypeServer": true,
"python.analysis.typeServerExecutable": "/opt/homebrew/bin/node",
"python.analysis.typeServerArguments": [
    "/Users/ringo/Repositories/pyright/packages/pyright-typeserver/pyright-typeserver.js",
    "--stdio"
],
"python.analysis.logTypeServerMessages": true
```

These settings are enabled in this workspace. They are experimental, require a trusted workspace, and the paths are machine-local.

Pylance 2026.3.1 does not reconstruct the new `typeArgs` field on TSP `TypeVarType`. The server can serialize `_ContainerT[Scalar[T]]`, but this Pylance client displays only `_ContainerT` or `Unknown`. Therefore this bridge is useful for protocol development but cannot provide correct HKT function hovers until Pylance adds matching client-side support.

After changing analyzer code:

1. Run the focused Jest test.
2. Run **Tasks: Run Task > Build Pyright type server**, or leave **Watch Pyright type server** running.
3. Restart Pylance with **Developer: Reload Window**. Reloading terminates the old TSP child process and launches the rebuilt bundle.
4. Use **View > Output > Pylance** to inspect protocol startup and messages.

Function-signature hovers also depend on the TSP representation of applied constructor variables. The protocol must serialize `_ContainerT[Scalar[T]]` with its `typeArgs`; otherwise Pylance can display only `_ContainerT`. The focused `typeServer.inProc.test` case named `getDeclaredType preserves applied TypeVar arguments` covers this boundary.

The watcher rebuilds the bundle, but a running Pylance process does not load changed JavaScript automatically. Reload after each bundle change that you want to exercise in the editor.

To inspect the bridge, open **View > Output**, select **Pylance**, and look for external type-server startup or TSP messages. Message logging is enabled in this workspace.

## Troubleshooting and rollback

- If hover still reports the published behavior, rebuild `packages/pyright-typeserver` and reload VS Code.
- If Pylance reports that the external server could not start, verify `/opt/homebrew/bin/node` and the wrapper path in `.vscode/settings.json`.
- The server requires `--stdio`; launching the wrapper without a transport exits immediately.
- `python.analysis.useNearestConfiguration` must remain enabled so the nested `pyarrow-cast/pyrightconfig.json` controls the prototype and its adjacent `pyarrow` package wins normal import discovery.
- Do not add `pyarrow-stubs` to `python.analysis.extraPaths` for this prototype.
- To return to Pylance's bundled type engine, set `python.analysis.enableExternalTypeServer` to `false` and reload the window.
