"""Кастомные исключения пакета ``openweather``.

Все ошибки, возникающие при работе с OpenWeather API, оборачиваются в
иерархию исключений с общим базовым классом :class:`OpenWeatherError`,
что позволяет пользователю отлавливать их одним ``except``.
"""


class OpenWeatherError(Exception):
    """Базовое исключение всех ошибок пакета ``openweather``."""


class InvalidUnitError(OpenWeatherError, ValueError):
    """Передана неподдерживаемая единица измерения температуры."""


class ApiRequestError(OpenWeatherError):
    """HTTP-запрос к OpenWeather API завершился ошибкой (сеть, статус)."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"OpenWeather API вернул код {status_code}: {message}")
        self.status_code = status_code


class ApiKeyError(ApiRequestError):
    """API-ключ отсутствует, невалиден или превышен лимит запросов."""


class CityNotFoundError(OpenWeatherError):
    """Город (или координаты) не найден в базе OpenWeather."""


class InvalidCoordinatesError(OpenWeatherError, ValueError):
    """Некорректные значения широты/долготы."""
