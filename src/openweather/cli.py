"""Интерфейс командной строки пакета.

Позволяет запрашивать текущую погоду без написания кода::

    export OPENWEATHER_API_KEY=...
    openweather Moscow --unit celsius
"""

from __future__ import annotations

import argparse
import os
import sys

from .client import OpenWeatherClient
from .exceptions import OpenWeatherError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openweather",
        description="Получить текущую погоду и прогноз через OpenWeather API.",
    )
    parser.add_argument("city", nargs="?", help="Название города (например, Moscow).")
    parser.add_argument(
        "--key",
        default=os.environ.get("OPENWEATHER_API_KEY"),
        help="API-ключ OpenWeather (или переменная OPENWEATHER_API_KEY).",
    )
    parser.add_argument(
        "--lat", type=float, default=None, help="Широта (для запроса по координатам)."
    )
    parser.add_argument(
        "--lon", type=float, default=None, help="Долгота (для запроса по координатам)."
    )
    parser.add_argument(
        "--unit",
        default="celsius",
        choices=("celsius", "kelvin", "fahrenheit"),
        help="Единица измерения температуры (по умолчанию: celsius).",
    )
    parser.add_argument(
        "--lang", default="ru", help="Язык описаний погоды (по умолчанию: ru)."
    )
    parser.add_argument("--forecast", action="store_true", help="Показать прогноз.")
    return parser


def main(argv=None) -> int:
    """Точка входа консольного скрипта. Возвращает код завершения."""
    args = _build_parser().parse_args(argv)

    if not args.key:
        print(
            "Ошибка: не передан API-ключ. Используйте --key или OPENWEATHER_API_KEY.",
            file=sys.stderr,
        )
        return 2

    client = OpenWeatherClient(api_key=args.key, unit=args.unit, lang=args.lang)
    try:
        if args.forecast:
            forecast = client.get_forecast(city=args.city, lat=args.lat, lon=args.lon)
            print(f"Прогноз: {forecast.city or 'по координатам'}")
            for item in forecast.items:
                print(
                    f"  {item.timestamp}: {item.temperature:g}° "
                    f"({item.description})"
                )
        else:
            weather = client.get_current_weather(
                city=args.city, lat=args.lat, lon=args.lon
            )
            city = weather.city or "По координатам"
            print(f"Погода: {city}")
            print(f"  Температура: {weather.temperature:g}°")
            print(f"  Ощущается: {weather.feels_like:g}°")
            print(f"  Влажность: {weather.humidity}%")
            print(f"  Давление: {weather.pressure} гПа")
            print(f"  Описание: {weather.description}")
    except OpenWeatherError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
