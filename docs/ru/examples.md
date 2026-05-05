# Практические примеры использования

## Создание простых задач

Создайте файл `simple_tasks.json`:

```json
[
  {
    "project": {"key": "MYPRJ"},
    "summary": "Настроить мониторинг системы",
    "issuetype": {"name": "Task"}
  },
  {
    "project": {"key": "MYPRJ"},
    "summary": "Исправить ошибку в авторизации",
    "issuetype": {"name": "Bug"},
    "priority": {"name": "High"}
  }
]
```

Создайте задачи:

```bash
tirajira import simple_tasks.json
```

## Создание задач с привязкой к эпику

```json
[
  {
    "project": {"key": "DEV"},
    "summary": "Реализовать функцию экспорта данных",
    "issuetype": {"name": "Story"},
    "epic_key": "DEV-123"
  }
]
```

## Создание задач для разных исполнителей

```json
[
  {
    "project": {"key": "BACK"},
    "summary": "Оптимизировать запросы к БД",
    "issuetype": {"name": "Task"},
    "assignee": {"emailAddress": "backend-dev@company.com"}
  },
  {
    "project": {"key": "FRONT"},
    "summary": "Исправить отображение формы",
    "issuetype": {"name": "Bug"},
    "assignee": {"emailAddress": "frontend-dev@company.com"}
  }
]
```

## Создание задач с кастомными полями

```json
[
  {
    "project": {"key": "PROJ"},
    "summary": "Задача с кастомными полями",
    "issuetype": {"name": "Task"},
    "customfield_10001": "Высокая",
    "customfield_10002": "Backend"
  }
]
```

Чтобы узнать ID кастомных полей, откройте настройки полей в Jira или используйте Jira API.

## Работа с отчетами

```bash
# Создание задач с сохранением отчета
tirajira import tasks.json --report

# Возобновление выполнения неудачных задач
tirajira resume tirajira_report_20231201_153045.json

# Извлечение неудачных задач в новый файл
tirajira extract-failed report.json failed_tasks.json
```

## Массовое создание задач

Для создания большого количества задач рекомендуется:

1. Разбить задачи на файлы по 50-100 штук
2. Использовать управление ограничением частоты запросов:

```bash
tirajira import large_tasks.json --max-concurrent-requests 5 --min-request-interval 2.0
```

## Создание багов

```json
[
  {
    "project": {"key": "QA"},
    "summary": "Исправление бага с авторизацией",
    "description": "Исправить проблему с авторизацией пользователей в мобильном приложении",
    "issuetype": {"name": "Bug"},
    "assignee": {"emailAddress": "developer@company.com"},
    "priority": {"name": "Critical"},
    "epic_key": "QA-50",
    "labels": ["bug", "auth", "mobile"]
  }
]
```