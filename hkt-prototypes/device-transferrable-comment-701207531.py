# https://github.com/python/typing/issues/548#issuecomment-701207531
from __future__ import annotations

from typing import reveal_type


class Device:
    ...

class CPU(Device):
    ...

class GPU(Device):
    ...


class DeviceTransferable[DeviceT: Device]:
    def __init__(self, device: type[DeviceT]):
        self.device = device

    def to_device[DeviceTransferableT: DeviceTransferable[DeviceT], NewDeviceT: Device](self: DeviceTransferableT[DeviceT], device: type[NewDeviceT]) -> DeviceTransferableT[NewDeviceT]:
        return type(self)(device=device)


class SomeOtherClass[DeviceT: Device](DeviceTransferable[DeviceT]):
    """Would prefer not to re-implement `to_device` in every inheriting class."""


reveal_type(SomeOtherClass(CPU).to_device(GPU), expected_text="SomeOtherClass[GPU]")
