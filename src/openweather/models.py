"""Типизированные модели данных ответов OpenWeather API.

Модели являются обычными :class:`dataclasses.dataclass` и не зависят от
HTTP-клиента, поэтому их удобно сериализовывать в dict и использовать
в собственных приложениях.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


def _to_dict(value: Any) -> Any:
    """Рекурсивно превратить dataclass (или коллекцию) в обычные dict."""
    if hasattr(value, "_asdict"):  # namedtuple и пр.
        return value._asdict()
    if isinstance(value, (list, tuple)):
        return [_to_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_dict(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    return value


@dataclass(frozen=True)
class Coordinates:
    """Географические координаты.

    Attributes:
        lat: широта.
        lon: долгота.
    """

    lat: float
    lon: float


@dataclass(frozen=True)
class WeatherCondition:
    """Описание погодного явления.

    Attributes:
        id: идентификатор условия (код OpenWeather).
        main: группа условий (``Clouds``, ``Rain`` и т. п.).
        description: человекочитаемое описание.
        icon: код иконки.
    """

    id: int
    main: str
    description: str
    icon: str


@dataclass
class CurrentWeather:
    """Текущая погода в выбранной точке.

    Attributes:
        temperature: температура в выбранной единице.
        feels_like: ощущаемая температура.
        humidity: относительная влажность, %.
        pressure: атмосферное давление, гПа.
        description: краткое описание погоды.
        condition: подробное условие (или ``None``).
        city: название города, если запрос был по имени.
        coordinates: координаты точки.
    """

    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    description: str
    condition: Optional[WeatherCondition] = None
    city: Optional[str] = None
    coordinates: Optional[Coordinates] = None

    def to_dict(self) -> Dict[str, Any]:
        """Сериализовать объект в обычный словарь."""
        return _to_dict(self)


@dataclass(frozen=True)
class ForecastItem:
    """Прогноз погоды на один интервал времени.

    Attributes:
        timestamp: Unix-время начала интервала.
        temperature: температура в выбранной единице.
        feels_like: ощущаемая температура.
        humidity: влажность, %.
        pressure: давление, гПа.
        description: описание погоды.
    """

    timestamp: int
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    description: str


@dataclass
class WeatherForecast:
    """Прогноз погоды на несколько интервалов.

    Attributes:
        city: название города (если известно).
        items: список интервалов прогноза.
    """

    city: Optional[str] = None
    items: List[ForecastItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Сериализовать объект в обычный словарь."""
        return _to_dict(self)
