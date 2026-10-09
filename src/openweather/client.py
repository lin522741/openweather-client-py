"""Основной клиент для работы с OpenWeather API.

Реализован поверх ``requests`` в тонкой обёртке: клиент принимает
API-ключ и желаемую единицу температуры, а методы возвращают типизированные
модели из :mod:`openweather.models`.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from .exceptions import (
    ApiKeyError,
    ApiRequestError,
    CityNotFoundError,
    InvalidCoordinatesError,
)
from .models import (
    Coordinates,
    CurrentWeather,
    ForecastItem,
    WeatherCondition,
    WeatherForecast,
)
from .units import TemperatureUnit, convert_temperature, resolve_unit

#: Базовый адрес OpenWeather API.
BASE_URL = "https://api.openweathermap.org/data/2.5"

#: Коды ответа, означающие проблемы с ключом/лимитом.
_KEY_ERROR_CODES = (401, 403)
#: Код ответа, означающий, что объект (город/координаты) не найден.
_NOT_FOUND_CODE = 404


class OpenWeatherClient:
    """Синхронный клиент OpenWeather API.

    Args:
        api_key: персональный ключ OpenWeather (обязателен).
        unit: единица измерения температуры. По умолчанию — цельсии.
            Принимает ``"celsius"``, ``"kelvin"``, ``"fahrenheit"`` и алиасы.
        lang: язык описаний погоды (например, ``"ru"``, ``"en"``).
        timeout: таймаут HTTP-запроса в секундах.
        session: готовый объект ``requests.Session`` (для переиспользования).

    Example:
        >>> client = OpenWeatherClient(api_key="...")
        >>> weather = client.get_current_weather(city="Moscow")
        >>> print(weather.temperature)
    """

    def __init__(
        self,
        api_key: str,
        unit: Optional[str] = None,
        lang: str = "ru",
        timeout: float = 10.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not api_key:
            raise ApiKeyError(401, "API-ключ OpenWeather не передан.")
        self.api_key = api_key
        self.unit = resolve_unit(unit)
        self.lang = lang
        self.timeout = timeout
        self.session = session or requests.Session()

    # ------------------------------------------------------------------
    # Публичное API
    # ------------------------------------------------------------------
    def get_current_weather(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ) -> CurrentWeather:
        """Получить текущую погоду по названию города или координатам.

        Args:
            city: название города (``"Moscow"``, ``"Лондон"``).
            lat: широта (если запрашиваете по координатам).
            lon: долгота (если запрашиваете по координатам).

        Returns:
            :class:`CurrentWeather` с температурой в выбранной единице.

        Raises:
            CityNotFoundError: город не найден.
            ApiKeyError: невалидный ключ или превышен лимит.
            ApiRequestError: прочие ошибки запроса.
        """
        params = self._build_params()
        self._apply_location(params, city, lat, lon)
        data = self._request("/weather", params)
        return self._parse_current_weather(data, city)

    def get_forecast(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        count: int = 8,
    ) -> WeatherForecast:
        """Получить прогноз погоды (интервалы по 3 часа).

        Args:
            city: название города.
            lat, lon: координаты.
            count: количество интервалов прогноза (по умолчанию 8 = 24 часа).

        Returns:
            :class:`WeatherForecast` со списком интервалов.
        """
        params = self._build_params()
        self._apply_location(params, city, lat, lon)
        params["cnt"] = count
        data = self._request("/forecast", params)
        return self._parse_forecast(data, city)

    # ------------------------------------------------------------------
    # Внутренние помощники
    # ------------------------------------------------------------------
    def _build_params(self) -> Dict[str, Any]:
        return {
            "appid": self.api_key,
            "units": self.unit.api_unit,
            "lang": self.lang,
        }

    @staticmethod
    def _apply_location(
        params: Dict[str, Any],
        city: Optional[str],
        lat: Optional[float],
        lon: Optional[float],
    ) -> None:
        if city:
            params["q"] = city
            return
        if lat is None or lon is None:
            raise InvalidCoordinatesError(
                "Укажите название города (city) либо и широту, и долготу (lat, lon)."
            )
        params["lat"] = lat
        params["lon"] = lon

    def _request(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{BASE_URL}{path}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise ApiRequestError(0, f"Ошибка сети: {exc}") from exc

        if response.status_code == _NOT_FOUND_CODE:
            raise CityNotFoundError(
                "Запрошенный город или координаты не найдены в OpenWeather."
            )
        if response.status_code in _KEY_ERROR_CODES:
            raise ApiKeyError(
                response.status_code,
                "Невалидный API-ключ, либо превышен лимит запросов.",
            )
        if response.status_code != 200:
            raise ApiRequestError(response.status_code, response.text[:300])

        return response.json()

    # ------------------------------------------------------------------
    # Парсинг ответов
    # ------------------------------------------------------------------
    def _parse_current_weather(
        self, data: Dict[str, Any], city: Optional[str]
    ) -> CurrentWeather:
        main = data.get("main", {})
        coords = data.get("coord", {})
        condition = self._first_condition(data.get("weather"))

        return CurrentWeather(
            temperature=self._as_unit(main.get("temp")),
            feels_like=self._as_unit(main.get("feels_like")),
            humidity=main.get("humidity"),
            pressure=main.get("pressure"),
            description=condition.description if condition else "",
            condition=condition,
            city=city or data.get("name"),
            coordinates=(
                Coordinates(coords.get("lat"), coords.get("lon")) if coords else None
            ),
        )

    def _parse_forecast(
        self, data: Dict[str, Any], city: Optional[str]
    ) -> WeatherForecast:
        items = []
        for entry in data.get("list", []):
            main = entry.get("main", {})
            condition = self._first_condition(entry.get("weather"))
            items.append(
                ForecastItem(
                    timestamp=entry.get("dt"),
                    temperature=self._as_unit(main.get("temp")),
                    feels_like=self._as_unit(main.get("feels_like")),
                    humidity=main.get("humidity"),
                    pressure=main.get("pressure"),
                    description=condition.description if condition else "",
                )
            )
        return WeatherForecast(
            city=city or data.get("city", {}).get("name"), items=items
        )

    def _as_unit(self, kelvin_value: Optional[float]) -> float:
        """Перевести температуру из кельвинов в выбранную единицу."""
        return convert_temperature(kelvin_value, self.unit)

    @staticmethod
    def _first_condition(raw_weather: Any) -> Optional[WeatherCondition]:
        if not raw_weather:
            return None
        item = raw_weather[0]
        return WeatherCondition(
            id=item.get("id"),
            main=item.get("main"),
            description=item.get("description"),
            icon=item.get("icon"),
        )

    # Shortcut для удобства: тип единицы доступен наружу.
    @property
    def temperature_unit(self) -> TemperatureUnit:
        """Текущая единица измерения температуры клиента."""
        return self.unit
