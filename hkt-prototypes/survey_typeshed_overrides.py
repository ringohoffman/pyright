"""Survey typeshed for the workaround that type constructor parameters remove.

Two patterns are counted:

1. Redeclared overrides: a subclass restates a base-class method whose signature is
   identical except that the return type names the subclass instead of the base
   (e.g. ``OrderedDict.fromkeys`` restating ``dict.fromkeys``).

2. Silent erasure: a base-class method returns the base class applied to
   method-scoped type variables, and a subclass inherits it without an override
   (e.g. ``defaultdict.fromkeys``), so calls on the subclass lose the subclass.

Usage:
    python survey_typeshed_overrides.py <typeshed-root> [<typeshed-root> ...]
"""

from __future__ import annotations

import ast
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Method:
    name: str
    params: tuple[str, ...]  # annotation strings, excluding self/cls
    returns: str | None
    lineno: int


@dataclass
class ClassInfo:
    name: str
    module: str
    path: Path
    lineno: int
    bases: list[str]
    class_typevars: set[str]
    methods: dict[str, list[Method]] = field(default_factory=dict)


def _last_name(expr: ast.expr) -> str | None:
    if isinstance(expr, ast.Name):
        return expr.id
    if isinstance(expr, ast.Attribute):
        return expr.attr
    if isinstance(expr, ast.Subscript):
        return _last_name(expr.value)
    return None


def _names_in(expr: ast.expr | None) -> set[str]:
    if expr is None:
        return set()
    return {n.id for n in ast.walk(expr) if isinstance(n, ast.Name)}


def _unparse(expr: ast.expr | None) -> str | None:
    return ast.unparse(expr) if expr is not None else None


def collect(path: Path, module: str, typevars: set[str], classes: list[ClassInfo]) -> None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return

    # Module-level TypeVar declarations.
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            if _last_name(node.value.func) in {"TypeVar", "ParamSpec", "TypeVarTuple"}:
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        typevars.add(t.id)

    def visit_class(node: ast.ClassDef) -> None:
        class_tvs: set[str] = set()
        for b in node.bases:
            class_tvs |= _names_in(b) & typevars
        for tp in getattr(node, "type_params", []):
            class_tvs.add(tp.name)

        info = ClassInfo(
            name=node.name,
            module=module,
            path=path,
            lineno=node.lineno,
            bases=[b for b in (_last_name(b) for b in node.bases) if b],
            class_typevars=class_tvs,
        )

        def add_method(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            args = fn.args
            positional = args.posonlyargs + args.args
            if positional and positional[0].arg in {"self", "cls"}:
                positional = positional[1:]
            params = tuple(
                _unparse(a.annotation) or "?"
                for a in positional + args.kwonlyargs
            )
            if args.vararg:
                params += (f"*{_unparse(args.vararg.annotation)}",)
            if args.kwarg:
                params += (f"**{_unparse(args.kwarg.annotation)}",)
            info.methods.setdefault(fn.name, []).append(
                Method(fn.name, params, _unparse(fn.returns), fn.lineno)
            )

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                add_method(item)
            elif isinstance(item, ast.If):
                # sys.version_info branches
                for sub in ast.walk(item):
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub in item.body + item.orelse:
                        add_method(sub)
            elif isinstance(item, ast.ClassDef):
                visit_class(item)

        classes.append(info)

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            visit_class(node)
        elif isinstance(node, ast.If):
            for sub in node.body + node.orelse:
                if isinstance(sub, ast.ClassDef):
                    visit_class(sub)


def main(roots: list[str], verify: bool = False) -> None:
    typevars: set[str] = set()
    classes: list[ClassInfo] = []

    for root in roots:
        for path in sorted(Path(root).rglob("*.pyi")):
            module = ".".join(path.relative_to(root).with_suffix("").parts)
            collect(path, module, typevars, classes)

    by_name: dict[str, list[ClassInfo]] = defaultdict(list)
    for c in classes:
        by_name[c.name].append(c)

    def resolve(base: str, frm: ClassInfo) -> ClassInfo | None:
        cands = by_name.get(base)
        if not cands:
            return None
        same = [c for c in cands if c.module == frm.module]
        return (same or cands)[0]

    def ancestors(c: ClassInfo, seen: set[int] | None = None) -> list[ClassInfo]:
        seen = seen if seen is not None else set()
        out: list[ClassInfo] = []
        for b in c.bases:
            r = resolve(b, c)
            if r is None or id(r) in seen or r is c:
                continue
            seen.add(id(r))
            out.append(r)
            out.extend(ancestors(r, seen))
        return out

    redeclared: list[tuple[ClassInfo, ClassInfo, Method, Method]] = []
    erased: list[tuple[ClassInfo, ClassInfo, Method]] = []
    seen_redeclared: set[tuple[str, str, int]] = set()

    for sub in classes:
        for base in ancestors(sub):
            if base.name == sub.name:
                continue
            for mname, base_methods in base.methods.items():
                sub_methods = sub.methods.get(mname)
                for bm in base_methods:
                    if not bm.returns or _last_name(ast.parse(bm.returns, mode="eval").body) != base.name:
                        continue
                    ret_names = _names_in(ast.parse(bm.returns, mode="eval").body)
                    method_tvs = (ret_names & typevars) - base.class_typevars
                    if not method_tvs:
                        continue  # Self would suffice; not our pattern
                    expected = bm.returns.replace(base.name, sub.name)
                    if sub_methods is None:
                        erased.append((sub, base, bm))
                        break
                    for sm in sub_methods:
                        key = (str(sub.path), sub.name, sm.lineno)
                        if sm.params == bm.params and sm.returns == expected and key not in seen_redeclared:
                            seen_redeclared.add(key)
                            redeclared.append((sub, base, sm, bm))

    def loc(c: ClassInfo, m: Method) -> str:
        return f"{c.path}:{m.lineno}"

    print(f"== Redeclared overrides (workaround applied): {len(redeclared)}")
    for sub, base, sm, bm in redeclared:
        print(f"  {sub.module}.{sub.name}.{sm.name}  restates  {base.module}.{base.name}.{bm.name}  -> {sm.returns}   [{loc(sub, sm)}]")

    print()
    print(f"== Inherited without override (subclass erased at call sites): {len(erased)}")
    for sub, base, bm in erased:
        print(f"  {sub.module}.{sub.name}.{bm.name}  inherits  {base.module}.{base.name}.{bm.name}  -> {bm.returns}   [{sub.path}:{sub.lineno}]")

    print()
    print(f"classes scanned: {len(classes)}, typevars: {len(typevars)}")

    if verify:
        verify_fromkeys(erased)


def _runtime_module(info: ClassInfo, roots: list[str]) -> str:
    parts = info.module.split(".")
    # Third-party stubs live under <root>/stubs/<distribution>/<package>/...; drop the distribution.
    if any(Path(r).name == "stubs" and str(info.path).startswith(str(Path(r))) for r in roots):
        parts = parts[1:]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def verify_fromkeys(erased: list[tuple[ClassInfo, ClassInfo, Method]]) -> None:
    """Call cls.fromkeys at runtime and report whether the subclass is preserved."""
    import importlib

    ok: list[str] = []
    wrong_type: list[str] = []
    raised: list[str] = []
    missing: list[str] = []

    for sub, base, bm in erased:
        if bm.name != "fromkeys":
            continue
        modname = _runtime_module(sub, _ROOTS)
        label = f"{modname}.{sub.name}"
        try:
            mod = importlib.import_module(modname)
            cls = getattr(mod, sub.name)
        except Exception as e:  # ImportError, AttributeError, anything on import
            missing.append(f"{label}  ({type(e).__name__})")
            continue
        try:
            result = cls.fromkeys(["k"])
        except Exception as e:
            raised.append(f"{label}  ({type(e).__name__}: {e})")
            continue
        (ok if type(result) is cls else wrong_type).append(f"{label}  -> {type(result).__name__}")

    print()
    print(f"== fromkeys runtime verification")
    print(f"   preserved subclass (real examples): {len(ok)}")
    for s in ok:
        print(f"     {s}")
    print(f"   returned a different type (not examples): {len(wrong_type)}")
    for s in wrong_type:
        print(f"     {s}")
    print(f"   raised (not usable via fromkeys): {len(raised)}")
    for s in raised:
        print(f"     {s}")
    print(f"   not importable here: {len(missing)}")
    for s in missing:
        print(f"     {s}")


_ROOTS: list[str] = []


if __name__ == "__main__":
    args = sys.argv[1:]
    _ROOTS = [a for a in args if a != "--verify"]
    main(_ROOTS, verify="--verify" in args)
