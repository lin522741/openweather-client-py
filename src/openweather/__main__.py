"""Запуск пакета через ``python -m openweather``."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
