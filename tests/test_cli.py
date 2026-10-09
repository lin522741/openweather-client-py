"""Тесты CLI-утилиты :mod:`openweather.cli`."""

from openweather import cli
from openweather.exceptions import CityNotFoundError


def test_missing_key_returns_2(capsys):
    code = cli.main(["Moscow"])  # без --key и без переменной окружения
    captured = capsys.readouterr()
    assert code == 2
    assert "API-ключ" in captured.err


def test_city_not_found_returns_1(monkeypatch, capsys):
    class _Client:
        def __init__(self, **kwargs):
            pass

        def get_current_weather(self, **kwargs):
            raise CityNotFoundError("Город не найден.")

    monkeypatch.setattr(cli, "OpenWeatherClient", _Client)
    code = cli.main(["Moscow", "--key", "k"])
    captured = capsys.readouterr()
    assert code == 1
    assert "Город не найден" in captured.err


def test_success_prints_weather(monkeypatch, capsys):
    class _Weather:
        city = "Moscow"
        temperature = 12.0
        feels_like = 10.0
        humidity = 70
        pressure = 1012
        description = "облачно"

    class _Client:
        def __init__(self, **kwargs):
            pass

        def get_current_weather(self, **kwargs):
            return _Weather()

    monkeypatch.setattr(cli, "OpenWeatherClient", _Client)
    code = cli.main(["Moscow", "--key", "k"])
    captured = capsys.readouterr()
    assert code == 0
    assert "Moscow" in captured.out
    assert "Температура: 12" in captured.out


def test_forecast_branch(monkeypatch, capsys):
    class _Item:
        timestamp = 1
        temperature = 5.0
        description = "туман"

    class _Forecast:
        city = "London"
        items = [_Item()]

    class _Client:
        def __init__(self, **kwargs):
            pass

        def get_forecast(self, **kwargs):
            return _Forecast()

    monkeypatch.setattr(cli, "OpenWeatherClient", _Client)
    code = cli.main(["London", "--key", "k", "--forecast"])
    captured = capsys.readouterr()
    assert code == 0
    assert "London" in captured.out
    assert "туман" in captured.out
