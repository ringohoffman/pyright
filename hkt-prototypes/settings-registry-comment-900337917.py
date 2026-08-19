# https://github.com/python/typing/issues/548#issuecomment-900337917

from __future__ import annotations

from abc import ABC

class SettingsRegistry[TSettings](ABC):
    @classmethod
    def from_serialized_settings[TSettingsRegistry: SettingsRegistry[TSettings]](cls: type[TSettingsRegistry[TSettings]], serialized_settings: list[str]) -> TSettingsRegistry[TSettings]:
        ...


class ConcreteSettingsRegistry[TSettings](SettingsRegistry[TSettings]):
    ...

reveal_type(ConcreteSettingsRegistry[int].from_serialized_settings([]), expected_text="ConcreteSettingsRegistry[int]")

# trivially solvable with Self type

from typing import Self


class SettingsRegistry2[TSettings](ABC):
    @classmethod
    def from_serialized_settings(cls, serialized_settings: list[str]) -> Self:
        ...


class ConcreteSettingsRegistry2[TSettings](SettingsRegistry2[TSettings]):
    ...

reveal_type(ConcreteSettingsRegistry2[int].from_serialized_settings([]), expected_text="ConcreteSettingsRegistry2[int]")
