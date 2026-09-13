# https://github.com/python/typing/issues/548#issuecomment-621790339
#
# Use case from Samuel Colvin (author of Pydantic) in async-redis:
# A command facade defines ~200 Redis operations (get, set, incr, etc.) implemented
# once in terms of a low-level `_execute(cmd, *args)`.
#
# In direct mode (`Redis`), each method returns an awaitable `Coroutine[Any, Any, T]`.
# In pipeline mode (`Pipeline`), operations are buffered and return `None`.
#
# Without HKT:
# To avoid copy-pasting 200 methods on both classes, you either need 200 separate
# TypeVars on a single class, or a code generator that duplicates stubs into a .pyi file.
#
# With HKT:
# A single generic `Commands[WrapperT[X]]` defines all operations once.
# Subclasses supply their wrapper constructor (`Result` vs `ConstNone`) and only implement `_execute`.

from collections.abc import Coroutine
from typing import Any, Protocol, reveal_type

type Result[T] = Coroutine[Any, Any, T]
type ConstNone[T] = None


class WrapperTemplate[T](Protocol):
    pass


class Commands[WrapperT[X: (bool, bytes, str, int, float, None)]: WrapperTemplate[X]]:
    def _execute(self, cmd: str, *args: Any) -> WrapperT[Any]:
        raise NotImplementedError

    def get(self, key: str) -> WrapperT[str]:
        return self._execute("GET", key)

    def set(self, key: str, value: str) -> WrapperT[bool]:
        return self._execute("SET", key, value)

    def incr(self, key: str) -> WrapperT[int]:
        return self._execute("INCR", key)


class Redis(Commands[Result]):
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def _execute(self, cmd: str, *args: Any) -> Result[Any]:
        async def _coro() -> Any:
            if cmd == "GET":
                return self._store.get(args[0])
            if cmd == "SET":
                self._store[args[0]] = args[1]
                return True
            if cmd == "INCR":
                val = int(self._store.get(args[0], "0")) + 1
                self._store[args[0]] = str(val)
                return val
            return None

        return _coro()


class Pipeline(Commands[ConstNone]):
    def __init__(self) -> None:
        self.buffer: list[tuple[str, tuple[Any, ...]]] = []

    def _execute(self, cmd: str, *args: Any) -> None:
        self.buffer.append((cmd, args))
        return None


# 1. Direct Redis client returns awaitable coroutines for each method's specific type
r = Redis()
reveal_type(r.get("key"), expected_text="Coroutine[Any, Any, str]")
reveal_type(r.set("key", "val"), expected_text="Coroutine[Any, Any, bool]")
reveal_type(r.incr("key"), expected_text="Coroutine[Any, Any, int]")

# 2. Pipeline client reuses the exact same methods, but all return None and buffer commands
p = Pipeline()
reveal_type(p.get("key"), expected_text="None")
reveal_type(p.set("key", "val"), expected_text="None")
reveal_type(p.incr("key"), expected_text="None")

