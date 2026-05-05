# Подготовка файлов с задачами

Создайте файл с задачами в любом из поддерживаемых форматов. Ниже представлены минимальные примеры для каждого формата:

## Минимальный пример (JSON)

Создайте файл `tasks.json`:

```json
[
  {
    "project": {"key": "PROJ"},
    "summary": "Моя первая задача",
    "issuetype": {"name": "Task"}
  },
  {
    "project": {"key": "PROJ"},
    "summary": "Исправление бага",
    "issuetype": {"name": "Bug"},
    "priority": {"name": "High"}
  }
]
```

## Расширенный пример (JSON)

```json
[
  {
    "project": {"key": "PROJ"},
    "summary": "Настройка CI/CD",
    "description": "Настроить непрерывную интеграцию для проекта",
    "issuetype": {"name": "Task"},
    "assignee": {"emailAddress": "developer@company.com"},
    "priority": {"name": "High"},
    "epic_key": "PROJ-100",
    "labels": ["devops", "ci-cd"],
    "customfield_10001": "Backend Team"
  }
]
```

## Примеры других форматов

### YAML

```yaml
- project:
    key: PROJ
  summary: Моя первая задача
  issuetype:
    name: Task
- project:
    key: PROJ
  summary: Исправление бага
  issuetype:
    name: Bug
  priority:
    name: High
```

### CSV

```csv
project.key,summary,issuetype.name
PROJ,Моя первая задача,Task
PROJ,Исправление бага,Bug
```

### Excel

Создайте таблицу Excel с заголовками в первой строке:
| project.key | summary | issuetype.name |
|-------------|---------|----------------|
| PROJ | Моя первая задача | Task |
| PROJ | Исправление бага | Bug |

Готовые примеры находятся в директории `examples/` проекта.

## Обязательные поля

Каждая задача должна содержать как минимум:
- `project.key` - ключ проекта в Jira
- `summary` - название задачи
- `issuetype.name` - тип задачи (Task, Bug, Story и т.д.)

## Полезные поля

- `description` - описание задачи
- `assignee.emailAddress` - email исполнителя
- `priority.name` - приоритет (Highest, High, Medium, Low, Lowest)
- `epic_key` - ключ эпика для автоматической привязки
- `labels` - массив меток (в JSON/YAML) или через точечную нотацию в CSV
- Кастомные поля: `customfield_XXXXX` (где XXXXX - ID поля в Jira)

## Подзадачи

Для создания подзадач укажите родительскую задачу через поле `parent.key`:

```json
{
  "project": {"key": "PROJ"},
  "summary": "Подзадача",
  "issuetype": {"name": "Sub-task"},
  "parent": {"key": "PROJ-123"}
}
```

## Привязка к эпику

После создания задачи TiraJira автоматически связывает её с эпикум, если указано поле `epic_key`:

```json
{
  "project": {"key": "PROJ"},
  "summary": "Задача в эпике",
  "issuetype": {"name": "Task"},
  "epic_key": "PROJ-100"  // ← Будет автоматически привязана к эпику
}
```

## Создание связей между задачами

TiraJira поддерживает создание связей между новыми и существующими задачами с помощью поля `linking`. Эта функция позволяет автоматически создавать связи различных типов между задачами после их создания.

### JSON

В JSON формате информация о связях указывается в поле `linking`:

```json
{
  "project": {"key": "PROJ"},
  "summary": "Задача со связью",
  "issuetype": {"name": "Task"},
  "linking": {
    "target_key": "PROJ-123",
    "link_type": "relates to"
  }
}
```

Вы также можете указать несколько связей:

```json
{
  "project": {"key": "PROJ"},
  "summary": "Задача с несколькими связями",
  "issuetype": {"name": "Task"},
  "linking": [
    {
      "target_key": "PROJ-123",
      "link_type": "relates to"
    },
    {
      "target_key": "PROJ-456",
      "link_type": "blocks"
    }
  ]
}
```

### YAML

В YAML формате структура аналогична JSON:

```yaml
project:
  key: PROJ
summary: Задача со связью
issuetype:
  name: Task
linking:
  target_key: PROJ-123
  link_type: relates to
```

Несколько связей:

```yaml
project:
  key: PROJ
summary: Задача с несколькими связями
issuetype:
  name: Task
linking:
  - target_key: PROJ-123
    link_type: relates to
  - target_key: PROJ-456
    link_type: blocks
```

### CSV

В CSV формате используется точечная нотация для указания информации о связях:

```csv
project.key,summary,issuetype.name,linking.target_key,linking.link_type
PROJ,Задача со связью,Task,PROJ-123,relates to
```

Для нескольких связей можно использовать индексацию:

```csv
project.key,summary,issuetype.name,linking.0.target_key,linking.0.link_type,linking.1.target_key,linking.1.link_type
PROJ,Задача с несколькими связями,Task,PROJ-123,relates to,PROJ-456,blocks
```

### Excel

В Excel формате также используется точечная нотация в заголовках столбцов:

| project.key | summary | issuetype.name | linking.target_key | linking.link_type |
|-------------|---------|----------------|--------------------|-------------------|
| PROJ | Задача со связью | Task | PROJ-123 | relates to |

Для нескольких связей:

| project.key | summary | issuetype.name | linking.0.target_key | linking.0.link_type | linking.1.target_key | linking.1.link_type |
|-------------|---------|----------------|----------------------|---------------------|----------------------|---------------------|
| PROJ | Задача с несколькими связями | Task | PROJ-123 | relates to | PROJ-456 | blocks |

### XML

В XML формате информация о связях указывается внутри элемента `linking`:

```xml
<issue>
  <project>
    <key>PROJ</key>
  </project>
  <summary>Задача со связью</summary>
  <issuetype>
    <name>Task</name>
  </issuetype>
  <linking>
    <target_key>PROJ-123</target_key>
    <link_type>relates to</link_type>
  </linking>
</issue>
```

Несколько связей:

```xml
<issue>
  <project>
    <key>PROJ</key>
  </project>
  <summary>Задача с несколькими связями</summary>
  <issuetype>
    <name>Task</name>
  </issuetype>
  <linking>
    <link>
      <target_key>PROJ-123</target_key>
      <link_type>relates to</link_type>
    </link>
    <link>
      <target_key>PROJ-456</target_key>
      <link_type>blocks</link_type>
    </link>
  </linking>
</issue>
```

## Типы связей и их валидация

TiraJira автоматически проверяет типы связей перед созданием. Приложение получает список допустимых типов связей из вашей Jira инстанции и сверяет с указанными в файле. Если подключение к Jira недоступно, используется набор распространенных типов связей:

- Blocks / Is Blocked By (Блокирует / Заблокирована)
- Relates / Is Related To (Относится к)
- Clones / Is Cloned By (Клонирует / Клонирована)
- Duplicate / Is Duplicate Of (Дублирует / Дубликат)
- Depends / Is Dependent On (Зависит от)
- Parent / Child (Родительская / Дочерняя)

Если указанный тип связи не найден в списке допустимых, связь не будет создана, но это не приведет к ошибке всей операции создания задач.