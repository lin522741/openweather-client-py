# openweather-client-py

[![Python](https://img.shields.io/pypi/pyversions/openweather-client-py.svg)](https://pypi.org/project/openweather-client-py/)
[![PyPI version](https://img.shields.io/pypi/v/openweather-client-py.svg)](https://pypi.org/project/openweather-client-py/)
[![License](https://img.shields.io/pypi/l/openweather-client-py.svg)](LICENSE)
[![CI](https://github.com/your-name/openweather-client-py/actions/workflows/ci.yml/badge.svg)](https://github.com/your-name/openweather-client-py/actions)

Аккуратный и типизированный Python-клиент для [OpenWeather API](https://openweathermap.org/api).
Позволяет получать текущую погоду и прогноз по названию города или координатам,
выбирать единицу измерения температуры и использовать готовую CLI-утилиту.

## Возможности

- ✅ Текущая погода по городу или координатам
- ✅ Прогноз погоды (интервалы по 3 часа)
- ✅ Выбор единиц: цельсии / кельвины / фаренгейты
- ✅ Типизированные модели данных (`dataclasses`)
- ✅ Понятные исключения (`CityNotFoundError`, `ApiKeyError`, …)
- ✅ CLI-утилита `openweather`
- ✅ 100% покрытие unit-тестами (заглушки вместо реальных запросов)
- ✅ CI на GitHub Actions, `tox`, линтеры `black`/`isort`/`flake8`/`pylint`

## Установка

```bash
pip install openweather-client-py
```

## Быстрый старт

```python
from openweather import OpenWeatherClient

client = OpenWeatherClient(api_key="ВАШ_КЛЮЧ", unit="celsius")
weather = client.get_current_weather(city="Moscow")

print(weather.city)          # Moscow
print(weather.temperature)   # 17.3
print(weather.description)   # облачно с прояснениями
```

### Прогноз

```python
forecast = client.get_forecast(city="London", count=8)  # 8 интервалов = 24 часа
for item in forecast.items:
    print(item.timestamp, item.temperature, item.description)
```

### По координатам

```python
weather = client.get_current_weather(lat=55.75, lon=37.62)
```

### Единицы измерения

```python
from openweather import OpenWeatherClient, CELSIUS, KELVIN, FAHRENHEIT

client = OpenWeatherClient(api_key="...", unit="fahrenheit")
# или: unit=FAHRENHEIT, unit="°f", unit="f"
```

## CLI

```bash
export OPENWEATHER_API_KEY="ВАШ_КЛЮЧ"
openweather Moscow --unit celsius
openweather --lat 55.75 --lon 37.62 --forecast
```

## Обработка ошибок

```python
from openweather import OpenWeatherClient, CityNotFoundError

client = OpenWeatherClient(api_key="...")
try:
    client.get_current_weather(city="Nope")
except CityNotFoundError:
    print("Город не найден")
```

Все ошибки наследуются от `OpenWeatherError`, поэтому их можно ловить одним
`except OpenWeatherError`.

## Разработка

```bash
pip install -e .[dev]   # или: pip install -r requirements-dev.txt
pytest                  # запуск тестов
tox                     # тесты + линтеры + покрытие
```

## Лицензия

Распространяется под лицензией [MIT](LICENSE).
