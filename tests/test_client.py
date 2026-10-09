"""Тесты HTTP-клиента :mod:`openweather.client` с заглушками запросов."""

import pytest
import requests

from openweather import OpenWeatherClient
from openweather.exceptions import (
    ApiKeyError,
    ApiRequestError,
    CityNotFoundError,
    InvalidCoordinatesError,
)
from openweather.models import Coordinates

CURRENT_PAYLOAD = {
    "coord": {"lat": 55.75, "lon": 37.62},
    "weather": [{"id": 803, "main": "Clouds", "description": "облачно", "icon": "04n"}],
    "main": {
        "temp": 285.15,
        "feels_like": 283.15,
        "humidity": 70,
        "pressure": 1012,
    },
    "name": "Moscow",
}

FORECAST_PAYLOAD = {
    "city": {"name": "London"},
    "list": [
        {
            "dt": 1600000000,
            "main": {
                "temp": 283.15,
                "feels_like": 281.15,
                "humidity": 60,
                "pressure": 1010,
            },
            "weather": [
                {"id": 500, "main": "Rain", "description": "дождь", "icon": "10d"}
            ],
        }
    ],
}


@pytest.fixture
def client():
    return OpenWeatherClient(api_key="test-key", unit="celsius")


def test_get_current_weather_by_city(client, requests_mock):
    requests_mock.get(
        "https://api.openweathermap.org/data/2.5/weather",
        json=CURRENT_PAYLOAD,
    )
    weather = client.get_current_weather(city="Moscow")

    assert weather.city == "Moscow"
    assert weather.temperature == pytest.approx(12.0)
    assert weather.feels_like == pytest.approx(10.0)
    assert weather.humidity == 70
    assert weather.description == "облачно"
    assert weather.coordinates == Coordinates(lat=55.75, lon=37.62)

    req = requests_mock.request_history[-1]
    assert (
        req.qs["q"][0].lower() == "moscow"
    )  # requests_mock приводит значение к нижнему регистру
    assert req.qs["appid"] == ["test-key"]
    assert req.qs["units"] == ["metric"]


def test_get_current_weather_by_coordinates(client, requests_mock):
    requests_mock.get(
        "https://api.openweathermap.org/data/2.5/weather", json=CURRENT_PAYLOAD
    )
    client.get_current_weather(lat=55.75, lon=37.62)
    req = requests_mock.request_history[-1]
    assert req.qs["lat"] == ["55.75"]
    assert req.qs["lon"] == ["37.62"]


def test_missing_location_raises(client, requests_mock):
    requests_mock.get(
        "https://api.openweathermap.org/data/2.5/weather", json=CURRENT_PAYLOAD
    )
    with pytest.raises(InvalidCoordinatesError):
        client.get_current_weather()


def test_city_not_found(client, requests_mock):
    requests_mock.get(
        "https://api.openweathermap.org/data/2.5/weather",
        status_code=404,
        json={"message": "city not found"},
    )
    with pytest.raises(CityNotFoundError):
        client.get_current_weather(city="Nowhere")


def test_bad_key(client, requests_mock):
    requests_mock.get(
        "https://api.openweathermap.org/data/2.5/weather",
        status_code=401,
        json={"message": "Invalid API key"},
    )
    with pytest.raises(ApiKeyError):
        client.get_current_weather(city="Moscow")


def test_generic_http_error(client, requests_mock):
    requests_mock.get(
        "https://api.openweathermap.org/data/2.5/weather",
        status_code=500,
        text="boom",
    )
    with pytest.raises(ApiRequestError):
        client.get_current_weather(city="Moscow")


def test_network_error(client, requests_mock):
    requests_mock.get(
        "https://api.openweathermap.org/data/2.5/weather",
        exc=requests.ConnectionError("no route"),
    )
    with pytest.raises(ApiRequestError):
        client.get_current_weather(city="Moscow")


def test_get_forecast(client, requests_mock):
    requests_mock.get(
        "https://api.openweathermap.org/data/2.5/forecast", json=FORECAST_PAYLOAD
    )
    forecast = client.get_forecast(city="London", count=8)
    assert forecast.city == "London"
    assert len(forecast.items) == 1
    item = forecast.items[0]
    assert item.temperature == pytest.approx(10.0)
    assert item.description == "дождь"

    req = requests_mock.request_history[-1]
    assert req.qs["cnt"] == ["8"]


def test_empty_api_key_raises():
    with pytest.raises(ApiKeyError):
        OpenWeatherClient(api_key="")


def test_temperature_unit_property(client):
    assert client.temperature_unit.name == "celsius"


def test_current_weather_without_condition(client, requests_mock):
    payload = dict(CURRENT_PAYLOAD)
    payload["weather"] = []
    requests_mock.get("https://api.openweathermap.org/data/2.5/weather", json=payload)
    weather = client.get_current_weather(city="Moscow")
    assert weather.condition is None
    assert weather.description == ""


def test_forecast_item_without_condition(client, requests_mock):
    payload = {
        "city": {"name": "Paris"},
        "list": [
            {
                "dt": 1,
                "main": {
                    "temp": 280.0,
                    "feels_like": 279.0,
                    "humidity": 50,
                    "pressure": 1000,
                },
                "weather": [],
            }
        ],
    }
    requests_mock.get("https://api.openweathermap.org/data/2.5/forecast", json=payload)
    forecast = client.get_forecast(city="Paris")
    assert forecast.items[0].description == ""
