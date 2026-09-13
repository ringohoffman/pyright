# https://github.com/python/typing/issues/548#issuecomment-701207531
#
# Use case from @florensacc:
# Generic container types that transfer across computation devices (CPU, GPU, TPU),
# or dtype transitions (int, float), common in PyTorch tensors and NumPy arrays.
#
# Without HKT:
# A base `DeviceTransferable[DeviceT]` cannot express `to_device(NewDevice) -> SelfT[NewDevice]`
# without subclasses having to reimplement `to_device` across every leaf class.
#
# With HKT:
# `to_device` is defined once on `DeviceTransferable` using self-type constructor polymorphism:
# `def to_device[SelfT: DeviceTransferable[DeviceT], NewDeviceT: Device](self: SelfT[DeviceT], device: type[NewDeviceT]) -> SelfT[NewDeviceT]`
# Subclasses (e.g. Tensor, Parameter, Buffer) inherit `to_device` preserving their exact type constructor.

from abc import ABC
from typing import ClassVar, cast, reveal_type


class Device(ABC):
    device_name: ClassVar[str]


class CPU(Device):
    device_name = "CPU"


class GPU(Device):
    device_name = "GPU"


class DeviceTransferable[DeviceT: Device]:
    def __init__(self, device: type[DeviceT]) -> None:
        self.device = device

    def to_device[SelfT: DeviceTransferable[DeviceT], NewDeviceT: Device](
        self: SelfT[DeviceT],
        device: type[NewDeviceT],
    ) -> SelfT[NewDeviceT]:
        inst = object.__new__(type(self))
        inst.__dict__.update(self.__dict__)
        inst.device = device
        return cast(SelfT[NewDeviceT], inst)


class Tensor[DeviceT: Device](DeviceTransferable[DeviceT]):
    def __init__(self, data: list[float], device: type[DeviceT]) -> None:
        super().__init__(device)
        self.data = data

    def compute(self) -> str:
        return f"Tensor({self.data}, device={self.device.device_name})"


# 1. Base method transfers device while preserving the derived Tensor constructor
t_cpu = Tensor([1.0, 2.0], CPU)
reveal_type(t_cpu, expected_text="Tensor[CPU]")

t_gpu = t_cpu.to_device(GPU)
reveal_type(t_gpu, expected_text="Tensor[GPU]")

# 2. Subclass-specific methods and data remain intact on transferred instance
assert t_gpu.compute() == "Tensor([1.0, 2.0], device=GPU)"
assert type(t_gpu) is Tensor
