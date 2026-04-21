"""
Модуль для отображения справочной информации по утилите TiraJira.
"""

from .. import __version__


def display_help() -> None:
    """Отображает справочную информацию по утилите."""
    help_text = f"""
TiraJira (тиражира) - инструмент для автоматизации массового создания задач в Jira.

Описание:
  Утилита позволяет создавать задачи в Jira из файлов JSON, YAML, CSV или Excel.
  Поддерживает привязку задач к эпикам и логирование процесса создания задач.

Форматы поддерживаемых файлов:
  - JSON (.json)
  - YAML (.yaml, .yml)
  - CSV (.csv)
  - Excel (.xlsx)

Использование:
  python3 main.py <путь_к_файлу>
  python3 main.py --help
  python3 main.py --version

Примеры:
  # Создание задач из JSON файла
  python3 main.py tasks.json

  # Создание задач из YAML файла
  python3 main.py tasks.yaml

  # Создание задач из CSV файла
  python3 main.py tasks.csv

  # Создание задач из Excel файла
  python3 main.py tasks.xlsx

  # Отображение справки
  python3 main.py --help

  # Отображение версии
  python3 main.py --version

Версия: {__version__}

Дополнительная информация:
  Перед использованием необходимо настроить параметры подключения к Jira в файле .env
  Скопируйте .env.example в .env и заполните своими данными.
"""
    print(help_text)
