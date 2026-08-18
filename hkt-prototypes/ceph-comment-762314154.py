# https://github.com/python/typing/issues/548#issuecomment-762314154

from __future__ import annotations

from typing import reveal_type


class HostSpec:
    ...


class DaemonDescription(object):
    ...


class ServiceDescription(object):
    ...


class InventoryFilter(object):
    ...


class InventoryHost(object):
    ...



class _Promise(object):
    ...


class Completion[T](_Promise):
    @property
    def result(self) -> T:
        ...


class IntCompletion(Completion[int]):
    ...


class Orchestrator[CompletionT[T]: Completion[T]]:
    def add_host(self, host_spec: HostSpec) -> CompletionT[str]:
        ...

    def remove_host(self, host: str) -> CompletionT[str]:
        ...

    def update_host_addr(self, host: str, addr: str) -> CompletionT[str]:
        ...

    def get_hosts(self) -> CompletionT[list[HostSpec]]:
        ...

    def add_host_label(self, host: str, label: str) -> CompletionT[str]:
        ...

    def remove_host_label(self, host: str, label: str) -> CompletionT[str]:
        ...

    def get_inventory(self, host_filter: InventoryFilter | None = None, refresh: bool = False) -> CompletionT[list[InventoryHost]]:
        ...

    def describe_service(self, service_type: str | None = None, service_name: str | None = None, refresh: bool = False) -> CompletionT[list[ServiceDescription]]:
        ...

    def list_daemons(self, service_name: str | None = None, daemon_type: str | None = None, daemon_id: str | None = None, host: str | None = None, refresh: bool = False) -> CompletionT[list[DaemonDescription]]:
        ...


class AsyncOrchestrator(Orchestrator[Completion]):
    ...


async_orch = AsyncOrchestrator()
reveal_type(async_orch.add_host(HostSpec()), expected_text="Completion[str]")
reveal_type(async_orch.get_hosts(), expected_text="Completion[list[HostSpec]]")
