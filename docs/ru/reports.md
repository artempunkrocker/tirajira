# Формат отчетов

TiraJira генерирует подробные отчеты о процессе создания задач для последующего анализа и возможного возобновления выполнения.

## Структура отчета

Отчеты содержат информацию о всех задачах, над которыми производилась работа, включая успешно созданные, неудачные и пропущенные задачи.

```json
{
  "report_metadata": {
    "generated_at": "2024-01-15T10:30:00Z",
    "tirajira_version": "1.2.0",
    "source_file": "tasks.json",
    "total_tasks": 100,
    "successful_tasks": 95,
    "failed_tasks": 5,
    "skipped_tasks": 0
  },
  "tasks": [
    {
      "index": 0,
      "input_data": {
        "project": {"key": "PROJ"},
        "summary": "Пример задачи",
        "issuetype": {"name": "Task"}
      },
      "status": "success",
      "created_issue_key": "PROJ-123",
      "created_at": "2024-01-15T10:30:01Z",
      "processing_time_ms": 150,
      "logs": []
    }
  ]
}
```

## Поля отчета

### report_metadata

- `generated_at` - Время генерации отчета в формате ISO 8601
- `tirajira_version` - Версия TiraJira, использованная для создания отчета
- `source_file` - Исходный файл с задачами
- `total_tasks` - Общее количество задач в исходном файле
- `successful_tasks` - Количество успешно созданных задач
- `failed_tasks` - Количество задач с ошибками
- `skipped_tasks` - Количество пропущенных задач

### task

- `index` - Порядковый номер задачи в исходном файле (начиная с 0)
- `input_data` - Исходные данные задачи как есть
- `status` - Статус обработки: `success`, `failed`, `skipped`
- `created_issue_key` - Ключ созданной задачи в Jira (только для успешных)
- `created_at` - Время создания задачи в Jira (только для успешных)
- `processing_time_ms` - Время обработки задачи в миллисекундах
- `error` - Информация об ошибке (только для неудачных)
- `logs` - Логи обработки задачи

## Поддерживаемые форматы отчетов

### JSON (по умолчанию)

Машиночитаемый формат с полной структурой данных. Используется по умолчанию при отсутствии указанного имени файла.

```bash
# Сохранить отчет в JSON
tirajira import tasks.json --report-file report.json
```

### CSV

Табличный формат, удобный для импорта в Excel или другие таблицы. Каждая строка соответствует одной задаче.

```bash
# Сохранить отчет в CSV
tirajira import tasks.json --report-file report.csv
```

### Excel (XLSX)

Формат Microsoft Excel с форматированием и несколькими листами (при необходимости).

```bash
# Сохранить отчет в Excel
tirajira import tasks.json --report-file report.xlsx
```

### YAML

Человекочитаемый формат, аналогичный JSON по структуре.

```bash
# Сохранить отчет в YAML
tirajira import tasks.json --report-file report.yaml
```

### XML

Формат с вложенными тегами, удобный для интеграций.

```bash
# Сохранить отчет в XML
tirajira import tasks.json --report-file report.xml
```

## Использование отчетов

### Возобновление выполнения

Используйте отчет для возобновления выполнения с места остановки:

```bash
# Возобновить выполнение из отчета
tirajira resume report.json
```

### Анализ ошибок

Просмотрите поле `error` в отчете для понимания причин неудач:

```json
{
  "error": {
    "type": "JiraApiError",
    "message": "Project PROJ does not exist",
    "details": {
      "status_code": 404,
      "response_body": "{\"errorMessages\":[\"No project could be found with key 'PROJ'.\"],\"errors\":{}}"
    }
  }
}
```

### Извлечение неудачных задач

Создайте новый файл только с неудавшимися задачами для повторной обработки:

```bash
# Извлечь неудавшиеся задачи
tirajira extract-failed report.json --output failed_tasks.json
```

## Автоматическое именование отчетов

Если имя файла отчета не указано явно, используется формат:

```
tirajira_report_YYYYMMDD_HHMMSS.json
```

Где:
- YYYYMMDD - дата в формате год/месяц/день
- HHMMSS - время в формате часы/минуты/секунды

## Настройка детализации отчета

Используйте флаг `--verbose` для более подробных отчетов:

```bash
# Подробный отчет с расширенной информацией
tirajira import tasks.json --verbose --report-file report.json
```