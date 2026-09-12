# https://github.com/python/typing/issues/548#issuecomment-1000492498
from collections.abc import Awaitable
from typing import Any, Protocol, reveal_type
import asyncio

type Identity[T] = T


# ==============================================================================
# Pattern 1: Sans-I/O Protocol Engine + Pluggable Transport (Real Production Design)
# ==============================================================================
# Real production libraries (HTTPX, redis-py, hyper-h2) avoid duplicating protocol
# logic across sync/async by using the "Sans-I/O" pattern:
#
# 1. `RedisProtocolParser`: Pure, CPU-bound protocol logic (RESP serialization &
#    deserialization). 100% shared, zero duplicate parsing logic.
# 2. `KVStore[WrapperT]`: High-level user API that encodes commands into wire bytes
#    via the parser and delegates I/O to a swappable `Transport[WrapperT]`.
# 3. `SyncSocketTransport` vs `AsyncSocketTransport`: ONLY handle actual network socket
#    I/O (e.g. `socket.socket` vs `asyncio.StreamReader/StreamWriter`). Zero command logic!

class RedisProtocolParser:
    """Pure Sans-I/O RESP (REdis Serialization Protocol) codec. Shared by sync and async."""

    @staticmethod
    def encode_command(cmd: str, *args: Any) -> bytes:
        parts = [cmd.encode("ascii")] + [
            a if isinstance(a, bytes) else str(a).encode("utf-8")
            for a in args if a is not None
        ]
        # RESP array: *<count>\r\n$<len>\r\n<data>\r\n...
        lines = [f"*{len(parts)}\r\n".encode("ascii")]
        for p in parts:
            lines.append(f"${len(p)}\r\n".encode("ascii") + p + b"\r\n")
        return b"".join(lines)

    @staticmethod
    def decode_response(data: bytes) -> tuple[Any, bytes]:
        if not data:
            return None, data
        prefix = data[:1]
        line_end = data.find(b"\r\n")
        if line_end == -1:
            return None, data
        payload = data[1:line_end]
        rest = data[line_end + 2:]

        if prefix == b"+":  # Simple string (e.g. +OK)
            return payload.decode("ascii") == "OK", rest
        elif prefix == b":":  # Integer (e.g. :10)
            return int(payload), rest
        elif prefix == b"$":  # Bulk string (e.g. $4\r\ntest\r\n or $-1)
            length = int(payload)
            if length == -1:
                return None, rest
            val = rest[:length]
            return val, rest[length + 2:]
        elif prefix == b"-":  # Error
            raise RuntimeError(payload.decode("utf-8"))
        return None, rest


class KVStore[WrapperT[T] = Identity[T]]:
    """Single unified client containing 100% of the API, validation, and serialization.

    Zero command or protocol code duplication between sync and async!
    """
    def __init__(self, namespace: str = "") -> None:
        self.namespace = namespace
        self._codec = RedisProtocolParser()

    def _send_wire_data(self, wire_data: bytes) -> WrapperT[bytes]:
        raise NotImplementedError

    def _format_key(self, key: str) -> str:
        if not key:
            raise ValueError("key cannot be empty")
        return f"{self.namespace}:{key}" if self.namespace else key

    def _dispatch(self, cmd: str, *args: Any) -> WrapperT[Any]:
        wire_bytes = self._codec.encode_command(cmd, *args)
        return self._send_wire_data(wire_bytes)

    def get(self, key: str) -> WrapperT[bytes | None]:
        full_key = self._format_key(key)
        return self._dispatch("GET", full_key)

    def set(self, key: str, value: bytes | str, ttl_seconds: int | None = None) -> WrapperT[bool]:
        full_key = self._format_key(key)
        val_bytes = value.encode("utf-8") if isinstance(value, str) else value
        return self._dispatch("SET", full_key, val_bytes, ttl_seconds)

    def incr(self, key: str, amount: int = 1) -> WrapperT[int]:
        full_key = self._format_key(key)
        return self._dispatch("INCRBY", full_key, amount)

    def exists(self, key: str) -> WrapperT[bool]:
        full_key = self._format_key(key)
        return self._dispatch("EXISTS", full_key)


class SyncKVStore(KVStore):
    """Synchronous backend: only implements raw socket wire I/O."""
    def __init__(self, host: str = "127.0.0.1", port: int = 6379, namespace: str = "") -> None:
        super().__init__(namespace=namespace)
        self.host = host
        self.port = port

    def _send_wire_data(self, wire_data: bytes) -> bytes:
        # Real driver: self._sock.sendall(wire_data); resp = self._sock.recv(4096)
        if b"GET" in wire_data:
            return b"$5\r\nvalue\r\n"
        elif b"SET" in wire_data:
            return b"+OK\r\n"
        elif b"INCRBY" in wire_data:
            return b":43\r\n"
        elif b"EXISTS" in wire_data:
            return b":1\r\n"
        return b"+OK\r\n"


class AsyncKVStore(KVStore[Awaitable]):
    """Asynchronous backend: only implements non-blocking stream wire I/O."""
    def __init__(self, host: str = "127.0.0.1", port: int = 6379, namespace: str = "") -> None:
        super().__init__(namespace=namespace)
        self.host = host
        self.port = port

    async def _send_wire_data(self, wire_data: bytes) -> bytes:
        # Real driver: self.writer.write(wire_data); await self.writer.drain(); resp = await self.reader.read(4096)
        await asyncio.sleep(0.001)  # Non-blocking network I/O
        if b"GET" in wire_data:
            return b"$5\r\nvalue\r\n"
        elif b"SET" in wire_data:
            return b"+OK\r\n"
        elif b"INCRBY" in wire_data:
            return b":43\r\n"
        elif b"EXISTS" in wire_data:
            return b":1\r\n"
        return b"+OK\r\n"


sync_store = SyncKVStore(namespace="app")
reveal_type(sync_store.get("session"), expected_text="bytes | None")
reveal_type(sync_store.set("session", "xyz"), expected_text="bool")
reveal_type(sync_store.incr("hits"), expected_text="int")
reveal_type(sync_store.exists("session"), expected_text="bool")

async_store = AsyncKVStore(namespace="app")
reveal_type(async_store.get("session"), expected_text="Awaitable[bytes | None]")
reveal_type(async_store.set("session", "xyz"), expected_text="Awaitable[bool]")
reveal_type(async_store.incr("hits"), expected_text="Awaitable[int]")
reveal_type(async_store.exists("session"), expected_text="Awaitable[bool]")


# ==============================================================================
# Pattern 2: Protocol / Interface Unification (Tishka17's Original Motivation)
# ==============================================================================
# In github issue #548, Tishka17 had two duplicate protocols:
#   class A(Protocol): def foo(self) -> int: ...
#   class AsyncA(Protocol): def foo(self) -> Awaitable[int]: ...
# With HKT, a single protocol describes both sync and async service interfaces:

class Service[WrapperT[T] = Identity[T]](Protocol):
    def get(self, key: str) -> WrapperT[bytes | None]: ...
    def exists(self, key: str) -> WrapperT[bool]: ...


# Concrete implementations satisfy the protocol for their respective WrapperT:
sync_svc = sync_store
reveal_type(sync_svc.get("session"), expected_text="bytes | None")
reveal_type(sync_svc.exists("session"), expected_text="bool")

async_svc: Service[Awaitable] = async_store
reveal_type(async_svc.get("session"), expected_text="Awaitable[bytes | None]")
reveal_type(async_svc.exists("session"), expected_text="Awaitable[bool]")


# ==============================================================================
# Pattern 3: Automatic Thread-Pool Adapter (Offloading Sync to Async)
# ==============================================================================
# If we have an existing sync implementation of `KVStore`, how can we realistically
# turn it into `KVStore[Awaitable]` at runtime? Wrap socket calls in `asyncio.to_thread`:

class ThreadedAsyncKVStore(KVStore[Awaitable]):
    def __init__(self, sync_store: SyncKVStore) -> None:
        super().__init__(namespace=sync_store.namespace)
        self._sync_store = sync_store

    def _send_wire_data(self, wire_data: bytes) -> Awaitable[bytes]:
        return asyncio.to_thread(self._sync_store._send_wire_data, wire_data)


threaded_store = ThreadedAsyncKVStore(sync_store)
reveal_type(threaded_store.get("session"), expected_text="Awaitable[bytes | None]")
reveal_type(threaded_store.set("session", "xyz"), expected_text="Awaitable[bool]")


# ==============================================================================
# Pattern 4: Partially Generic Type Constructors
# ==============================================================================
# Addressing: "what if we wanted to define it as a partially generic type constructor?"
#
# Q: Why `KVStore[Awaitable]` and not `KVStore[Awaitable[T]]`?
# A: `WrapperT[T]` expects a type constructor of kind (* -> *).
#    `Awaitable` is the constructor itself (like passing `func` to `map(func, list)`).
#    `Awaitable[T]` would have an unbound/dangling `T`.
#
# If you have a multi-parameter constructor (e.g. `tuple[Status, T]` or `Result[Error, T]`)
# and want to partially apply it, use a 1-parameter type alias:

type WithStatus[T] = tuple[int, T]  # Error/status fixed to int, payload generic T

class StatusKVStore(KVStore[WithStatus]):
    def __init__(self, sync_store: SyncKVStore) -> None:
        super().__init__(namespace=sync_store.namespace)
        self._sync_store = sync_store

    def _send_wire_data(self, wire_data: bytes) -> tuple[int, bytes]:
        result = self._sync_store._send_wire_data(wire_data)
        return 200, result


status_store = StatusKVStore(sync_store)
reveal_type(status_store.get("session"), expected_text="tuple[int, bytes | None]")
reveal_type(status_store.set("session", "xyz"), expected_text="tuple[int, bool]")
