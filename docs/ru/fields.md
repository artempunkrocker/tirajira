# Поддерживаемые поля задач

## Стандартные поля Jira

- `project.key` - ключ проекта (обязательно)
- `summary` - название задачи (обязательно)
- `description` - описание задачи
- `issuetype.name` - тип задачи (Task, Bug, Story и т.д.)
- `assignee.emailAddress` - email исполнителя
- `priority.name` - приоритет (Highest, High, Medium, Low, Lowest)
- `labels` - метки (массив для JSON/YAML, точки для CSV)
- `epic_key` - ключ эпика (специальное поле TiraJira, используется для автоматической привязки задачи к эпику после создания)
- `parent.key` - ключ родительской задачи (для подзадач)

## Кастомные поля

Вы можете использовать любые кастомные поля вашего Jira, указывая их ID:

- `customfield_10001`
- `customfield_10002`
- и т.д.

### Форматы кастомных полей

Разные типы кастомных полей требуют разного формата:

#### Текстовые поля
```json
"customfield_10001": "Текстовое значение"
```

#### Поля выбора (select)
```json
"customfield_10002": {"value": "Выбранное значение"}
```

#### Множественный выбор
```json
"customfield_10003": [{"value": "Значение 1"}, {"value": "Значение 2"}]
```

#### Пользовательские поля
```json
"customfield_10004": {"accountId": "user-account-id"}
```

#### Дата
```json
"customfield_10005": "2023-12-01"
```

## Как узнать ID полей

1. Перейдите в "Jira Administration" → "Issues" → "Custom Fields"
2. Найдите нужное поле и наведите на него мышь
3. ID будет отображен в URL или всплывающей подсказке
4. Или используйте Jira REST API: `GET /rest/api/2/field`

## Пример задачи со всеми типами полей

```json
[
  {
    "project": {"key": "PROJ"},
    "summary": "Задача с различными полями",
    "description": "Полный пример использования всех типов полей",
    "issuetype": {"name": "Task"},
    "assignee": {"emailAddress": "user@company.com"},
    "priority": {"name": "High"},
    "epic_key": "PROJ-100",
    "labels": ["example", "documentation"],
    "customfield_10001": "Текстовое значение",
    "customfield_10002": {"value": "Выбранное значение"},
    "customfield_10003": [{"value": "Значение 1"}, {"value": "Значение 2"}]
  }
]
```