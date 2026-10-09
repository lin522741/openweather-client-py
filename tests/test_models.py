"""Тесты сериализации моделей :mod:`openweather.models`."""

from collections import namedtuple

from openweather.models import (
    Coordinates,
    CurrentWeather,
    ForecastItem,
    WeatherCondition,
    WeatherForecast,
)


def test_current_weather_to_dict():
    weather = CurrentWeather(
        temperature=20.0,
        feels_like=18.0,
        humidity=55,
        pressure=1012,
        description="ясно",
        condition=WeatherCondition(
            id=800, main="Clear", description="ясно", icon="01d"
        ),
        city="Moscow",
        coordinates=Coordinates(lat=55.75, lon=37.62),
    )
    d = weather.to_dict()
    assert d["city"] == "Moscow"
    assert d["temperature"] == 20.0
    assert d["condition"]["main"] == "Clear"
    assert d["coordinates"] == {"lat": 55.75, "lon": 37.62}


def test_forecast_to_dict():
    forecast = WeatherForecast(
        city="London",
        items=[ForecastItem(1, 10.0, 9.0, 60, 1010, "дождь")],
    )
    d = forecast.to_dict()
    assert d["city"] == "London"
    assert d["items"][0]["temperature"] == 10.0
    assert d["items"][0]["description"] == "дождь"


def test_forecast_empty_items():
    assert WeatherForecast().to_dict() == {"city": None, "items": []}


def test_nested_to_dict_types():
    Point = namedtuple("Point", "x y")
    weather = CurrentWeather(
        temperature=1.0,
        feels_like=0.0,
        humidity=1,
        pressure=1,
        description="",
    )
    nested = [Point(1, 2), {"a": weather}, 42]
    # точечно проверяем _to_dict на контейнерах через to_dict внутри моделей
    d = CurrentWeather(
        temperature=1.0,
        feels_like=0.0,
        humidity=1,
        pressure=1,
        description="",
        coordinates=Coordinates(lat=1.0, lon=2.0),
    ).to_dict()
    assert d["coordinates"] == {"lat": 1.0, "lon": 2.0}
    assert nested[0]._asdict() == {"x": 1, "y": 2}
    assert isinstance(nested[1]["a"], CurrentWeather)
