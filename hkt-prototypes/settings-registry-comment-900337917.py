# https://github.com/python/typing/issues/548#issuecomment-900337917
#
# Use case from MischaPanch:
# Deserializing settings into a generic class hierarchy `SettingsRegistry[TSettings]`
# via a `@classmethod` factory `from_serialized_settings`.
#
# Context & Discussion:
# The author noted that deserializing settings dynamically in a classmethod
# while preserving both the subclass type and its parameter type (`TSettingsRegistry[TSettings]`)
# felt like it required higher-kinded typevars:
#     @classmethod
#     def from_serialized_settings[TSettingsRegistry: SettingsRegistry[TSettings]](
#         cls: type[TSettingsRegistry[TSettings]], serialized_settings: list[str]
#     ) -> TSettingsRegistry[TSettings]: ...
#
# Comparison with PEP 673 (`Self`):
# As demonstrated in Part 2 below, if the classmethod does NOT transform the element type
# (it retains the instance parameter `TSettings`), PEP 673's `Self` type already solves this
# without HKT:
#     @classmethod
#     def from_serialized_settings(cls, serialized_settings: list[str]) -> Self: ...
#
# However, if the classmethod were to infer or alter `TSettings` from the input
# (e.g. from an unspecialized constructor `cls: type[TSettingsRegistry[Any]]`),
# `Self` cannot express that transformation, and full HKT constructor parameterization is required.

from __future__ import annotations

from abc import ABC
from typing import Self, reveal_type


# 1. HKT Template-bound classmethod formulation
class SettingsRegistry[TSettings](ABC):
    def __init__(self, settings: list[TSettings]) -> None:
        self.settings = settings

    @classmethod
    def from_serialized_settings[TSettingsRegistry: SettingsRegistry[TSettings]](
        cls: type[TSettingsRegistry[TSettings]],
        serialized_settings: list[str],
    ) -> TSettingsRegistry[TSettings]:
        return cls([])


class ConcreteSettingsRegistry[TSettings](SettingsRegistry[TSettings]):
    pass


c1 = ConcreteSettingsRegistry[int].from_serialized_settings([])
reveal_type(c1, expected_text="ConcreteSettingsRegistry[int]")


# 2. Comparison: PEP 673 Self-type formulation
class SettingsRegistrySelf[TSettings](ABC):
    def __init__(self, settings: list[TSettings]) -> None:
        self.settings = settings

    @classmethod
    def from_serialized_settings(cls, serialized_settings: list[str]) -> Self:
        return cls([])


class ConcreteSettingsRegistrySelf[TSettings](SettingsRegistrySelf[TSettings]):
    pass


c2 = ConcreteSettingsRegistrySelf[int].from_serialized_settings([])
reveal_type(c2, expected_text="ConcreteSettingsRegistrySelf[int]")

# Runtime functional validation
assert isinstance(c1, ConcreteSettingsRegistry)
assert c1.settings == []
assert isinstance(c2, ConcreteSettingsRegistrySelf)
assert c2.settings == []
