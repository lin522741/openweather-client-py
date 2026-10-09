"""openweather — аккуратный клиент для OpenWeather API.

Библиотека предоставляет типизированный и простой в использовании доступ
к текущей погоде и прогнозу OpenWeather, поддерживает разные единицы
измерения температуры и консольную утилиту.

Пример использования::

    from openweather import OpenWeatherClient

    client = OpenWeatherClient(api_key="ваш-ключ", unit="celsius")
    weather = client.get_current_weather(city="Moscow")
    print(weather.temperature)
"""

from .client import OpenWeatherClient
from .exceptions import (
    ApiKeyError,
    ApiRequestError,
    CityNotFoundError,
    InvalidCoordinatesError,
    InvalidUnitError,
    OpenWeatherError,
)
from .models import (
    Coordinates,
    CurrentWeather,
    ForecastItem,
    WeatherCondition,
    WeatherForecast,
)
from .units import CELSIUS, FAHRENHEIT, KELVIN, TemperatureUnit

__version__ = "0.1.0"

__all__ = [
    "OpenWeatherClient",
    "OpenWeatherError",
    "ApiKeyError",
    "ApiRequestError",
    "CityNotFoundError",
    "InvalidCoordinatesError",
    "InvalidUnitError",
    "Coordinates",
    "CurrentWeather",
    "ForecastItem",
    "WeatherCondition",
    "WeatherForecast",
    "TemperatureUnit",
    "CELSIUS",
    "KELVIN",
    "FAHRENHEIT",
    "__version__",
]
