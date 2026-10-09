"""Тесты модуля :mod:`openweather.units`."""

import pytest

from openweather.exceptions import InvalidUnitError
from openweather.units import (
    CELSIUS,
    FAHRENHEIT,
    KELVIN,
    convert_temperature,
    resolve_unit,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, CELSIUS),
        ("celsius", CELSIUS),
        ("c", CELSIUS),
        ("°C", CELSIUS),
        ("kelvin", KELVIN),
        ("k", KELVIN),
        ("fahrenheit", FAHRENHEIT),
        ("f", FAHRENHEIT),
        ("°F", FAHRENHEIT),
    ],
)
def test_resolve_unit_ok(value, expected):
    assert resolve_unit(value) == expected


def test_resolve_unit_unknown_raises():
    with pytest.raises(InvalidUnitError):
        resolve_unit("parsecs")


def test_convert_kelvin_to_celsius():
    assert convert_temperature(273.15, CELSIUS) == pytest.approx(0.0)


def test_convert_kelvin_to_fahrenheit():
    assert convert_temperature(273.15, FAHRENHEIT) == pytest.approx(32.0)


def test_convert_kelvin_to_kelvin():
    assert convert_temperature(300.0, KELVIN) == pytest.approx(300.0)
