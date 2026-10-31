import importlib
import sys
from pathlib import Path

# Scan all packages / submodules in stdlib lib directory
stdlib_dir = Path(sys.base_prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}"
seen = set()
dict_subs = []

skip_prefixes = ("test", "_test", "idlelib", "tkinter")

for py_path in sorted(stdlib_dir.rglob("*.py")):
    rel_parts = py_path.relative_to(stdlib_dir).with_suffix("").parts
    if any(p.startswith(skip_prefixes) for p in rel_parts):
        continue
    mod_name = ".".join(rel_parts).replace(".__init__", "")
    try:
        mod = importlib.import_module(mod_name)
    except Exception:
        continue
    for attr in dir(mod):
        try:
            val = getattr(mod, attr)
            if isinstance(val, type) and issubclass(val, dict) and val is not dict:
                key = f"{val.__module__}.{val.__name__}"
                if key not in seen:
                    seen.add(key)
                    dict_subs.append((key, val))
        except Exception:
            pass

print(f"Total runtime dict subclasses discovered in stdlib lib/: {len(dict_subs)}")
for name, cls in sorted(dict_subs):
    try:
        res = cls.fromkeys(["k"])
        preserves = (type(res) is cls)
        ret_type = type(res).__name__
    except Exception as e:
        preserves = False
        ret_type = f"EXC: {type(e).__name__}"
    print(f"  {name:50s} | fromkeys -> {ret_type:20s} (preserves: {preserves})")
