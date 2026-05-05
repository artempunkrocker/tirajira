# Команды TiraJira

## Основные команды

### `import` - Создание задач

Создает задачи из файла:

```bash
# Базовое использование
tirajira import tasks.json

# Поддерживаются все форматы
tirajira import tasks.yaml
tirajira import tasks.csv
tirajira import tasks.xlsx
tirajira import tasks.xml
```

### `resume` - Возобновление выполнения

Продолжает выполнение из отчета, обрабатывая только неудачные задачи:

```bash
tirajira resume report.json
```

### `extract-failed` - Извлечение неудачных задач

Извлекает неудачные задачи из отчета в новый файл:

```bash
# Извлечение в формате JSON
tirajira extract-failed report.json failed_tasks.json

# Извлечение в формате YAML
tirajira extract-failed report.json failed_tasks.yaml

# Извлечение в формате CSV
tirajira extract-failed report.json failed_tasks.csv
```

## Параметры команд

### Управление ограничением частоты запросов

```bash
# Максимальное количество одновременных запросов к Jira API (по умолчанию: 5)
--max-concurrent-requests N, -mcr N

# Минимальный интервал между запросами в секундах (по умолчанию: 10.0)
--min-request-interval SECONDS, -mri SECONDS

# Время сброса квоты при неактивности в секундах (по умолчанию: 60.0)
--inactivity-reset-time SECONDS, -irt SECONDS
```

### Устаревшие параметры пакетной обработки

Следующие параметры устарели и будут удалены в будущих версиях:

```bash
# Размер пакета (устарело)
--batch-size N, -b N

# Задержка между пакетами в секундах (устарело)
--delay SECONDS, -d SECONDS
```

### Отчеты и логирование

```bash
# Сохранить отчет (автоматическое имя файла)
--report

# Сохранить отчет с указанным именем
--report report.json

# Подробное логирование
--verbose, -v
```

### Обработка ошибок

```bash
# Остановить при первой ошибке
--stop-on-error
```

## Практические примеры

```bash
# Создание задач с подробным логированием
tirajira import tasks.json --verbose

# Создание задач с ограничением частоты запросов
tirajira import tasks.json --max-concurrent-requests 3 --min-request-interval 15.0

# Создание задач с остановкой при ошибке и сохранением отчета
tirajira import tasks.json --stop-on-error --report

# Создание задач с отчетом в формате Excel
tirajira import tasks.json --report report.xlsx

# Возобновление выполнения с ограничением частоты запросов
tirajira resume report.json --max-concurrent-requests 3 --min-request-interval 15.0

# Возобновление выполнения с подробным логированием
tirajira resume report.json --verbose

# Возобновление выполнения с остановкой при ошибке
tirajira resume report.json --stop-on-error
```

## Получение справки

```bash
# Версия программы
tirajira --version

# Справка по всем командам
tirajira --help

# Справка по конкретной команде
tirajira import --help
tirajira resume --help
tirajira extract-failed --help
```