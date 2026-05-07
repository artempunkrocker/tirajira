# TiraJira (тиражира) - Автоматизация создания задач в Jira

## Быстрый старт

1. Установите TiraJira:
   ```bash
   pip3 install tirajira
   ```

2. Подготовьте файл с задачами в формате JSON:
   ```json
   [
     {
       "project": {"key": "PROJ"},
       "summary": "Первая задача",
       "description": "Описание первой задачи",
       "issuetype": {"name": "Task"}
     }
   ]
   ```

3. Создайте задачи в Jira:
   ```bash
   tirajira import tasks.json
   ```

Готово! Ваши задачи созданы в Jira.

## Системные требования

- Python 3.10 или выше
- Доступ к Jira Server
- API-токен для доступа к Jira

## Установка

Для обычных пользователей (рекомендуется):
```bash
pip3 install tirajira
```

Для разработчиков:
```bash
git clone https://github.com/ваш-логин/tirajira.git
cd tirajira
poetry install
```

[Подробнее об установке](installation.md)

## Настройка подключения к Jira

TiraJira поддерживает два режима аутентификации:
- **Jira Cloud** - Basic Auth (email + API token)
- **Jira Server/Data Center** - Personal Access Token

[Подробнее о настройке подключения](configuration.md)

## Подготовка файла с задачами

Поддерживаются форматы: JSON, YAML, CSV, Excel, XML

Минимальный пример (JSON):
```json
[
  {
    "project": {"key": "PROJ"},
    "summary": "Моя первая задача",
    "issuetype": {"name": "Task"}
  }
]
```

[Подробнее о форматах файлов](file_formats.md)

## Команды

- `import` - Создание задач из файла
- `resume` - Возобновление выполнения из отчета
- `extract-failed` - Извлечение неудачных задач из отчета

[Подробнее о командах](commands.md)

## Подробная документация

- [🔧 Установка и настройка](installation.md)
- [🔐 Настройка подключения к Jira](configuration.md)
- [📝 Подготовка файлов с задачами](file_formats.md)
- [🧰 Команды и параметры](commands.md)
- [💡 Практические примеры](examples.md)
- [📋 Поддерживаемые поля задач](fields.md)
- [🛑 Управление ограничением частоты запросов](rate_limiting.md)
- [❓ Решение частых проблем](troubleshooting.md)
- [🤔 Часто задаваемые вопросы](faq.md)
- [📊 Формат отчетов](reports.md)
- [👥 Участие в разработке](contributing.md)
- [🆘 Поддержка](support.md)
