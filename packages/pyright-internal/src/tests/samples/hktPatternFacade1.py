# This sample tests higher-kinded type constructor parameterization on a facade/service class (Ceph orchestrator pattern).

from __future__ import annotations

from typing import reveal_type


class HostSpec:
    pass


class _Promise:
    pass


class Completion[T](_Promise):
    @property
    def result(self) -> T:
        raise NotImplementedError


class DirectResult[T]:
    @property
    def result(self) -> T:
        raise NotImplementedError


class Orchestrator[CompletionT[T]: Completion[T]]:
    def add_host(self, host_spec: HostSpec) -> CompletionT[str]:
        raise NotImplementedError

    def get_hosts(self) -> CompletionT[list[HostSpec]]:
        raise NotImplementedError


class AsyncOrchestrator(Orchestrator[Completion]):
    pass


# This should generate an error because DirectResult does not derive from Completion.
class DirectOrchestrator(Orchestrator[DirectResult]):
    pass


class IntCompletion(Completion[int]):
    pass


# This should generate an error because IntCompletion is not a generic constructor (arity 0).
class IntOrchestrator(Orchestrator[IntCompletion]):
    pass


async_orch = AsyncOrchestrator()
reveal_type(async_orch.add_host(HostSpec()), expected_text="Completion[str]")
reveal_type(async_orch.get_hosts(), expected_text="Completion[list[HostSpec]]")

direct_orch = DirectOrchestrator()
reveal_type(direct_orch.add_host(HostSpec()), expected_text="DirectResult[str]")
reveal_type(direct_orch.get_hosts(), expected_text="DirectResult[list[HostSpec]]")
