# https://github.com/python/typing/issues/548#issuecomment-762314154
#
# Use case from Ceph orchestrator (https://github.com/ceph/ceph/pull/38953):
# Base `Orchestrator[CompletionT[T]: Completion[T]]` is generic over the completion constructor.
#
# Real typing benefits demonstrated here:
# 1. LSP compliance without # type: ignore:
#    `process(completions: list[CompletionT[object]])` in the base interface allows
#    subclasses to accept their specific completion list (`list[TestCompletion]`) without
#    violating the Liskov Substitution Principle (which required # type: ignore in ceph#38954).
# 2. Generic workflow type preservation:
#    Generic functions written against `Orchestrator[C]` preserve the concrete driver's
#    completion type `C[T]` rather than erasing to base `Completion[T]`.

import functools
from collections.abc import Callable
from typing import reveal_type


class HostSpec:
    def __init__(self, hostname: str) -> None:
        self.hostname = hostname


class _Promise:
    INITIALIZED = 1
    FINISHED = 2

    def __init__(self) -> None:
        self._state = self.INITIALIZED


class Completion[T](_Promise):
    def __init__(self, on_complete: Callable[[], T]) -> None:
        super().__init__()
        self._on_complete = on_complete
        self._result: T | None = None

    def finalize(self) -> None:
        self._result = self._on_complete()
        self._state = self.FINISHED

    @property
    def result(self) -> T:
        assert self._state == self.FINISHED
        assert self._result is not None
        return self._result


class TestCompletion[T](Completion[T]):
    def evaluate(self) -> None:
        self.finalize()

    @property
    def is_test(self) -> bool:
        return True


def deferred_op[T](f: Callable[..., T]) -> Callable[..., TestCompletion[T]]:
    """Ceph's decorator that wraps driver methods to return TestCompletion[T]."""
    @functools.wraps(f)
    def wrapper(*args: object, **kwargs: object) -> TestCompletion[T]:
        return TestCompletion(lambda: f(*args, **kwargs))
    return wrapper


class Orchestrator[CompletionT[T]: Completion[T]]:
    def add_host(self, host_spec: HostSpec) -> CompletionT[str]:
        raise NotImplementedError

    def get_hosts(self) -> CompletionT[list[HostSpec]]:
        raise NotImplementedError

    def process(self, completions: list[CompletionT[object]]) -> None:
        """Process pending completions. In subclasses, takes CompletionT without LSP violations."""
        raise NotImplementedError


class TestOrchestrator(Orchestrator[TestCompletion]):
    def __init__(self) -> None:
        self._hosts: list[HostSpec] = []

    @deferred_op
    def add_host(self, host_spec: HostSpec) -> str:
        self._hosts.append(host_spec)
        return f"added {host_spec.hostname}"

    @deferred_op
    def get_hosts(self) -> list[HostSpec]:
        return list(self._hosts)

    def process(self, completions: list[TestCompletion[object]]) -> None:
        for c in completions:
            c.evaluate()


# --- Benefit 1: Generic workflow over any Orchestrator preserves constructor C ---
def sync_host[C[T]: Completion[T]](orch: Orchestrator[C], hostname: str) -> C[str]:
    return orch.add_host(HostSpec(hostname))


orch = TestOrchestrator()

# Calling generic workflow sync_host preserves TestCompletion[str]!
completion = sync_host(orch, "node1")
reveal_type(completion, expected_text="TestCompletion[str]")
assert completion.is_test

# --- Benefit 2: Calling process() directly accepts specialized completions cleanly ---
hosts_comp = orch.get_hosts()
orch.process([completion, hosts_comp])

assert completion.result == "added node1"
assert len(hosts_comp.result) == 1 and hosts_comp.result[0].hostname == "node1"
