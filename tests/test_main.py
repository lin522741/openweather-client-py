"""Тест запуска пакета как модуля (``python -m openweather``)."""

import subprocess
import sys


def test_module_runs_via_python_m():
    result = subprocess.run(
        [sys.executable, "-m", "openweather", "Moscow"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    # Без ключа CLI должен вернуть код 2 с сообщением об ошибке.
    assert result.returncode == 2
    assert "API-ключ" in result.stderr
