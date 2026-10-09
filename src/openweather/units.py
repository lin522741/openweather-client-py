"""Работа с единицами измерения температуры.

OpenWeather по умолчанию возвращает температуру в кельвинах, но
поддерживает ``metric`` (цельсии) и ``imperial`` (фаренгейты). Модуль
предоставляет единый способ указать желаемую единицу и конвертировать
значения вручную.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .exceptions import InvalidUnitError

#: Система единиц, понимаемая OpenWeather API напрямую.
API_UNITS = ("standard", "metric", "imperial")

#: Легкочитаемые пользовательские обозначения единиц.
ALIASES = {
    "c": "celsius",
    "celsius": "celsius",
    "°c": "celsius",
    "k": "kelvin",
    "kelvin": "kelvin",
    "°k": "kelvin",
    "f": "fahrenheit",
    "fahrenheit": "fahrenheit",
    "°f": "fahrenheit",
}


@dataclass(frozen=True)
class TemperatureUnit:
    """Описание единицы измерения температуры.

    Attributes:
        name: каноническое имя единицы (``celsius``, ``kelvin``, ``fahrenheit``).
        api_unit: значение, передаваемое в OpenWeather
            (``metric``/``imperial``/``standard``).
    """

    name: str
    api_unit: str


CELSIUS = TemperatureUnit("celsius", "metric")
KELVIN = TemperatureUnit("kelvin", "standard")
FAHRENHEIT = TemperatureUnit("fahrenheit", "imperial")

#: Реестр доступных единиц по каноническому имени.
_REGISTRY = {unit.name: unit for unit in (CELSIUS, KELVIN, FAHRENHEIT)}


def resolve_unit(unit: Optional[str]) -> TemperatureUnit:
    """Привести пользовательское обозначение к :class:`TemperatureUnit`.

    Args:
        unit: обозначение единицы. Может быть ``None`` (вернёт цельсии),
            алиасом (``"c"``, ``"°F"``) или каноническим именем.

    Returns:
        Соответствующий :class:`TemperatureUnit`.

    Raises:
        InvalidUnitError: если единица не поддерживается.
    """
    if unit is None:
        return CELSIUS
    normalized = str(unit).strip().lower()
    if normalized in _REGISTRY:
        return _REGISTRY[normalized]
    if normalized in ALIASES:
        return _REGISTRY[ALIASES[normalized]]
    raise InvalidUnitError(
        f"Неизвестная единица температуры: {unit!r}. "
        f"Доступные: {', '.join(_REGISTRY)}."
    )


def convert_temperature(value_kelvin: float, unit: TemperatureUnit) -> float:
    """Конвертировать температуру из кельвинов в нужную единицу.

    Args:
        value_kelvin: температура в кельвинах.
        unit: целевая единица.

    Returns:
        Температура в целевой единице.
    """
    if unit.name == "celsius":
        return value_kelvin - 273.15
    if unit.name == "fahrenheit":
        return (value_kelvin - 273.15) * 9 / 5 + 32
    return value_kelvin
