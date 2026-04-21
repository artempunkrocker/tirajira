# TiraJira (тиражира) - Автоматизация создания задач в Jira

TiraJira - это мощная утилита командной строки для массового создания задач в Jira. Она позволяет загружать задачи из файлов разных форматов (JSON, YAML, CSV, Excel, XML) и автоматически создавать их в вашем Jira-проекте.

## Преимущества использования

- 🚀 **Массовое создание задач** - создавайте десятки и сотни задач за одну операцию
- 📁 **Поддержка разных форматов** - используйте JSON, YAML, CSV, Excel или XML файлы
- 🔗 **Привязка к эпикам** - автоматически связывайте задачи с эпиками
- ⚡ **Пакетная обработка** - оптимизированная отправка задач для максимальной производительности
- 🛠️ **Поддержка кастомных полей** - используйте любые поля вашего Jira
- 📊 **Подробное логирование** - отслеживайте процесс создания каждой задачи
- 🛑 **Режим остановки при ошибках** - прекращение обработки при возникновении ошибок (--stop-on-error)

## Системные требования

- Python 3.8 или выше
- Доступ к Jira Server
- API-токен для доступа к Jira

## Установка

### Вариант 1: Установка через pip (рекомендуется для пользователей)

1. Убедитесь, что на вашем компьютере установлен Python 3.8 или выше:

   ```bash
   python3 --version
   ```

2. Установите TiraJira как пакет Python:
   ```bash
   pip3 install tirajira
   ```

После установки вы сможете использовать утилиту из командной строки:
```bash
tirajira tasks.json
```

### Вариант 2: Установка для разработки через Poetry (рекомендуется для разработчиков)

1. Убедитесь, что на вашем компьютере установлен Python 3.8 или выше и Poetry:

   ```bash
   python3 --version
   poetry --version
   ```

   Если Poetry не установлен, установите его согласно [официальной документации](https://python-poetry.org/docs/#installation).

2. Скачайте проект TiraJira:

   ```bash
   git clone <URL_репозитория>
   cd tira-jira
   ```

3. Установите зависимости через Poetry:
   ```bash
   poetry install
   ```

4. Активируйте виртуальное окружение Poetry:
   ```bash
   poetry shell
   ```

## Сборка и установка из исходного кода

Если вы хотите собрать пакет самостоятельно из исходного кода:

1. Убедитесь, что установлен Poetry:
   ```bash
   poetry --version
   ```

2. Соберите пакет:
   ```bash
   poetry build
   ```

3. Установите собранный пакет:
   ```bash
   pip3 install dist/tirajira-*.whl
   ```

   Или установите в режиме разработки:
   ```bash
   pip3 install -e .
   ```

После установки вы сможете использовать утилиту из командной строки:

```bash
tirajira tasks.json
tirajira tasks.yaml
tirajira tasks.csv
tirajira tasks.xlsx
tirajira tasks.xml
```

Также можно установить пакет в режиме разработки:

```bash
pip3 install -e .
```

## Настройка подключения к Jira

TiraJira поддерживает два режима аутентификации: базовую аутентификацию (Basic Auth) и аутентификацию через Personal Access Token (PAT).
Выберите подходящий режим в зависимости от типа вашего Jira (Cloud или Server) и политик безопасности.

**Важно:** Для корректной работы приложения необходимо указать все обязательные параметры для выбранного режима аутентификации.
При отсутствии обязательных параметров программа выведет информативное сообщение об ошибке.

### Режим 1: Базовая аутентификация (Basic Auth) - для Jira Cloud

**Обязательные параметры:**

- `JIRA_SERVER` - адрес вашего Jira сервера
- `JIRA_EMAIL` - ваш email в Jira
- `JIRA_API_TOKEN` - API токен для доступа к Jira

1. Создайте файл `.env` в корневой директории проекта:

   ```bash
   cp .env.example .env
   ```

2. Откройте файл `.env` в текстовом редакторе и заполните следующие параметры:

   ```env
   JIRA_SERVER=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   ```

3. Как получить API-токен:
   - Перейдите в настройки вашего профиля Jira
   - Выберите "Security" → "API tokens"
   - Нажмите "Create API token"
   - Сохраните токен и вставьте его в файл `.env`

### Режим 2: Аутентификация через Personal Access Token (PAT) - для Jira Server

**Обязательные параметры:**

- `JIRA_SERVER` - адрес вашего Jira сервера
- `JIRA_PAT_TOKEN` - Personal Access Token для доступа к Jira Server

1. Создайте файл `.env` в корневой директории проекта:

   ```bash
   cp .env.example .env
   ```

2. Откройте файл `.env` в текстовом редакторе и заполните следующие параметры:

   ```env
   JIRA_SERVER=https://your-jira-server.com
   JIRA_PAT_TOKEN=your-personal-access-token
   ```

3. Как получить Personal Access Token:
   - Перейдите в настройки вашего профиля Jira Server
   - Выберите "Personal Access Tokens"
   - Нажмите "Create token"
   - Укажите имя токена и срок действия
   - Сохраните токен и вставьте его в файл `.env`

Обратите внимание: если в конфигурации присутствует переменная `JIRA_PAT_TOKEN`,
то будет использоваться режим аутентификации через Personal Access Token.
В противном случае применяется базовая аутентификация.

## Подготовка файла с задачами

TiraJira поддерживает пять форматов файлов для описания задач:

### Формат JSON

Создайте файл `tasks.json` со следующей структурой:

```json
[
  {
    "project": { "key": "PROJ" },
    "summary": "Название задачи",
    "description": "Подробное описание задачи",
    "issuetype": { "name": "Task" },
    "assignee": { "name": "assignee@example.com" },
    "priority": { "name": "Medium" },
    "epic_key": "PROJ-100",
    "labels": ["label1", "label2"],
    "customfield_10001": "Значение кастомного поля"
  }
]
```

Готовые примеры файлов можно найти в директории `examples/` проекта:

- `examples/example_tasks.json` - пример JSON файла
- `examples/example_tasks.yaml` - пример YAML файла
- `examples/example_tasks.csv` - пример CSV файла
- `examples/example_tasks.xlsx` - пример Excel файла

### Формат YAML

Создайте файл `tasks.yaml`:

```yaml
- project:
    key: PROJ
  summary: Название задачи
  description: Подробное описание задачи
  issuetype:
    name: Task
  assignee:
    emailAddress: assignee@example.com
  priority:
    name: Medium
  epic_key: PROJ-100
  labels:
    - label1
    - label2
  customfield_10001: Значение кастомного поля
```

### Формат CSV

Создайте файл `tasks.csv` с заголовками в первой строке:

```csv
project.key,summary,description,issuetype.name,assignee.emailAddress,priority.name,epic_key,labels.0,labels.1,customfield_10001
PROJ,"Название задачи","Описание задачи",Task,assignee@example.com,Medium,PROJ-100,label1,label2,"Значение кастомного поля"
```

### Формат Excel

Создайте файл `tasks.xlsx` с таблицей:

- Первая строка содержит заголовки полей
- Каждая следующая строка - отдельная задача
- Поддерживаются те же поля, что и в CSV

Готовый пример Excel файла можно найти в `examples/example_tasks.xlsx`.

### Формат XML

Создайте файл `tasks.xml` со следующей структурой:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<issues>
  <issue>
    <project>
      <key>PROJ</key>
    </project>
    <summary>Название задачи</summary>
    <description>Подробное описание задачи</description>
    <issuetype>
      <name>Task</name>
    </issuetype>
    <assignee>
      <emailAddress>assignee@example.com</emailAddress>
    </assignee>
    <priority>
      <name>Medium</name>
    </priority>
    <epic_key>PROJ-100</epic_key>
    <labels>
      <item>label1</item>
      <item>label2</item>
    </labels>
    <customfield_10001>Значение кастомного поля</customfield_10001>
  </issue>
</issues>
```

Готовый пример XML файла можно найти в `examples/example_tasks.xml`.

## Запуск утилиты

После подготовки файла с задачами, запустите TiraJira с помощью одной из доступных команд:

### Команда import

Импортирует и создает задачи из файла:

```bash
tirajira import путь/к/файлу.json
```

Поддерживаются все пять форматов:

```bash
tirajira import tasks.json
tirajira import tasks.yaml
tirajira import tasks.csv
tirajira import tasks.xlsx
tirajira import tasks.xml
```

### Команда extract-failed

Извлекает неудачные задачи из отчета и сохраняет их в указанный файл:

```bash
tirajira extract-failed путь/к/отчету.json путь/к/выходному/файлу.json
```

Поддерживаются различные форматы выходных файлов:

```bash
# Извлечение в формате JSON
tirajira extract-failed report.json failed_tasks.json

# Извлечение в формате YAML
tirajira extract-failed report.json failed_tasks.yaml

# Извлечение в формате CSV
tirajira extract-failed report.json failed_tasks.csv
```

### Команда resume

Продолжает выполнение из отчета, обрабатывая только неудачные задачи:

```bash
tirajira resume путь/к/отчету.json
```

### Дополнительные параметры

Вы можете настроить параметры пакетной обработки для команд `import` и `resume`:

- `--batch-size` или `-b` - размер пакета для обработки задач (по умолчанию: 10)
- `--delay` или `-d` - задержка между пакетами в секундах (по умолчанию: 1.0)
- `--stop-on-error` - прекратить обработку при возникновении ошибки
- `--report [FILE]` - сохранить машинночитаемый отчет о выполнении (если FILE не указан, имя файла генерируется автоматически)
- `--verbose` или `-v` - включить подробный режим логирования

Примеры использования:

```bash
# Запуск команды import с размером пакета 5 и задержкой 2 секунды
tirajira import tasks.json --batch-size 5 --delay 2.0

# Запуск команды import с сокращенными параметрами
tirajira import tasks.json -b 20 -d 0.5

# Запуск команды import с остановкой при ошибке
tirajira import tasks.json --stop-on-error

# Запуск команды import с сохранением отчета с автоматическим именем файла
tirajira import tasks.json --report

# Запуск команды import с сохранением отчета с указанным именем файла
tirajira import tasks.json --report execution_report.json

# Запуск команды import с сохранением отчета в формате Excel
tirajira import tasks.json --report execution_report.xlsx

# Запуск команды import с сохранением отчета в формате CSV
tirajira import tasks.json --report execution_report.csv

# Запуск команды resume с остановкой при ошибке
tirajira resume report.json --stop-on-error

# Запуск команды resume с подробным логированием
tirajira resume report.json --verbose
```

Для получения версии утилиты используйте флаг `--version` или `-v`:

```bash
tirajira --version
tirajira -v
```

## Примеры использования

Готовые примеры файлов можно найти в директории `examples/` проекта. Для запуска примеров используйте следующие команды:

### Базовые примеры

```bash
# Запуск команды import с JSON файлом
tirajira import examples/example_tasks.json

# Запуск команды import с YAML файлом
tirajira import examples/example_tasks.yaml

# Запуск команды import с CSV файлом
tirajira import examples/example_tasks.csv
```

### Пример использования команды extract-failed

```bash
# Извлечение неудачных задач из отчета
tirajira extract-failed report.json failed_tasks.json
```

### Пример использования команды resume

```bash
# Продолжение выполнения из отчета
tirajira resume report.json
```

### Базовый пример

Создание нескольких задач из JSON файла:

```json
[
  {
    "project": { "key": "DEV" },
    "summary": "Настройка CI/CD для проекта Альфа",
    "description": "Настроить непрерывную интеграцию и доставку для проекта Альфа",
    "issuetype": { "name": "Task" },
    "assignee": { "emailAddress": "developer@example.com" },
    "priority": { "name": "High" },
    "epic_key": "DEV-100"
  },
  {
    "project": { "key": "DEV" },
    "summary": "Обновление документации API",
    "description": "Обновить документацию REST API в соответствии с последними изменениями",
    "issuetype": { "name": "Task" },
    "assignee": { "emailAddress": "techwriter@example.com" },
    "priority": { "name": "Medium" },
    "epic_key": "DEV-101"
  }
]
```

Запуск:

```bash
tirajira tasks.json
```

### Создание багов

```json
[
  {
    "project": { "key": "QA" },
    "summary": "Исправление бага с авторизацией",
    "description": "Исправить проблему с авторизацией пользователей в мобильном приложении",
    "issuetype": { "name": "Bug" },
    "assignee": { "emailAddress": "developer@example.com" },
    "priority": { "name": "Critical" },
    "epic_key": "QA-50",
    "labels": ["bug", "auth", "mobile"]
  }
]
```

### Использование кастомных полей

```json
[
  {
    "project": { "key": "PROJ" },
    "summary": "Задача с кастомными полями",
    "description": "Пример использования кастомных полей",
    "issuetype": { "name": "Task" },
    "customfield_10001": "Бизнес-ценность: Высокая",
    "customfield_10002": "Команда: Разработка",
    "customfield_10003": { "value": "Feature" }
  }
]
```

## Поддерживаемые поля задач

### Стандартные поля Jira

- `project.key` - ключ проекта (обязательно)
- `summary` - название задачи (обязательно)
- `description` - описание задачи
- `issuetype.name` - тип задачи (Task, Bug, Story и т.д.)
- `assignee.emailAddress` - email исполнителя
- `priority.name` - приоритет (Highest, High, Medium, Low, Lowest)
- `labels` - метки (массив для JSON/YAML, точки для CSV)
- `epic_key` - ключ эпика (специальное поле TiraJira, используется для автоматической привязки задачи к эпику после создания)

### Кастомные поля

Вы можете использовать любые кастомные поля вашего Jira, указывая их ID:

- `customfield_10001`
- `customfield_10002`
- и т.д.

## Формат отчетов

При использовании параметра `--report` TiraJira создает машинночитаемый отчет в различных форматах в зависимости от расширения указанного файла. Поддерживаются следующие форматы:

- JSON (по умолчанию, если расширение не указано)
- CSV
- Excel (формат XLSX)
- YAML
- XML

Если имя файла отчета не указано явно, то используется формат JSON с автоматически сгенерированным именем файла вида `tirajira_report_YYYYMMDD_HHMMSS.json`.

### Структура отчета

Отчет состоит из двух основных разделов:

1. **metadata** - общая информация об операции:
   - `generated_at` - дата и время создания отчета (в формате ISO 8601)
   - `source_file` - путь к исходному файлу с задачами
   - `jira_server` - URL сервера Jira (из переменной окружения JIRA_SERVER)
   - `total_tasks` - общее количество задач в исходном файле
   - `successful_tasks` - количество успешно созданных задач
   - `failed_tasks` - количество задач, при создании которых произошли ошибки

2. **tasks** - детализированная информация по каждой задаче:
   - `id` - порядковый номер задачи в исходном файле (начиная с 0)
   - `status` - статус обработки ("success" или "failure")
   - `issue_key` - ключ созданной задачи в Jira (только для успешно созданных задач)
   - `error_message` - сообщение об ошибке (только для задач с ошибками)
   - `issue_data` - исходные данные задачи из файла
   - `processed_at` - дата и время обработки задачи (в формате ISO 8601)
   - `issue_url` - полный URL задачи в Jira (только для успешно созданных задач)

### Пример отчета в формате JSON

```json
{
  "metadata": {
    "generated_at": "2023-12-01T15:30:45.123456",
    "source_file": "tasks.json",
    "jira_server": "https://your-domain.atlassian.net",
    "total_tasks": 2,
    "successful_tasks": 1,
    "failed_tasks": 1
  },
  "tasks": [
    {
      "id": 0,
      "status": "success",
      "issue_key": "PROJ-123",
      "issue_data": {
        "project": { "key": "PROJ" },
        "summary": "Название задачи",
        "description": "Описание задачи",
        "issuetype": { "name": "Task" }
      },
      "processed_at": "2023-12-01T15:30:45.123456",
      "issue_url": "https://your-domain.atlassian.net/browse/PROJ-123"
    },
    {
      "id": 1,
      "status": "failure",
      "error_message": "Project key 'INVALID' does not exist",
      "issue_data": {
        "project": { "key": "INVALID" },
        "summary": "Задача с некорректным проектом",
        "issuetype": { "name": "Task" }
      },
      "processed_at": "2023-12-01T15:30:45.234567"
    }
  ]
}
```

### Формат отчета в Excel

Отчет в формате Excel представляет собой файл с двумя листами:

1. **Metadata** - лист с общей информацией об операции в формате таблицы ключ-значение
2. **Tasks** - лист с детальной информацией по каждой задаче в табличном формате, где:
   - Каждая строка представляет отдельную задачу
   - Каждая колонка представляет отдельное поле задачи
   - Вложенные структуры преобразуются в плоский формат с использованием точечной нотации (например, `issue_data.project.key`)

### Использование отчетов

Отчеты могут быть полезны для:

- Анализа результатов массового создания задач
- Автоматической обработки результатов выполнения
- Интеграции с другими системами
- Отладки и устранения ошибок при создании задач

Примеры использования различных форматов отчетов:

```bash
# Отчет в формате JSON (по умолчанию)
tirajira tasks.json --report

# Отчет в формате JSON с явным указанием имени файла
tirajira tasks.json --report execution_report.json

# Отчет в формате CSV
tirajira tasks.json --report execution_report.csv

# Отчет в формате Excel
tirajira tasks.json --report execution_report.xlsx

# Отчет в формате YAML
tirajira tasks.json --report execution_report.yaml

# Отчет в формате XML
tirajira tasks.json --report execution_report.xml
```

## Частые ошибки и их решение

### "Ошибка при создании задачи: You must specify a summary of the issue"

Убедитесь, что каждая задача имеет поле `summary` с непустым значением.

### "Ошибка при создании задачи: Project key is required"

Проверьте, что у каждой задачи есть поле `project.key`.

### "Ошибка при создании задачи: Issue type is required"

Убедитесь, что у каждой задачи указан тип задачи в поле `issuetype.name`.

### "Ошибка аутентификации"

Проверьте правильность параметров в файле `.env`:

- `JIRA_SERVER` - должен быть правильным URL вашего Jira
- `JIRA_EMAIL` - должен быть действующим email
- `JIRA_API_TOKEN` - должен быть действующим API токеном

### "Файл не найден"

Проверьте правильность пути к файлу с задачами.

## Рекомендации по использованию

1. **Тестирование перед массовым созданием**
   - Создавайте сначала одну тестовую задачу
   - Проверяйте, что все поля заполняются корректно
   - Затем переходите к массовому созданию

2. **Использование эпиков**
   - Указывайте существующие ключи эпиков
   - Если эпик еще не создан, создайте его отдельно

3. **Работа с большими объемами**
   - Для более 20 задач рекомендуется разбивать на несколько файлов
   - Между пакетами задач добавляйте паузу во избежание ограничений API

4. **Именование файлов**
   - Используйте понятные имена файлов
   - Храните файлы в отдельной директории для истории

5. **Резервное копирование**
   - Сохраняйте файлы с задачами как историю созданных задач
   - Это поможет при необходимости восстановить или повторить операции

6. **Использование отчетов**
   - Используйте параметр `--report` для получения машинночитаемого отчета о выполнении
   - Отчеты позволяют анализировать результаты выполнения и интегрироваться с другими системами
   - Поддерживаются различные форматы отчетов: JSON, CSV, Excel, YAML и XML
   - При автоматическом формировании имени файла отчет будет иметь вид `tirajira_report_YYYYMMDD_HHMMSS.json`
   - Выбор формата осуществляется по расширению указанного файла отчета

## Версионирование

Проект использует автоматическое версионирование на основе [Conventional Commits](https://www.conventionalcommits.org/) с помощью [poetry-dynamic-versioning](https://github.com/mtkennerly/poetry-dynamic-versioning).

Версия формируется автоматически на основе истории коммитов и тегов Git. При сборке пакета Poetry будет использовать актуальную версию, рассчитанную на основе ваших коммитов.

Для помощи в создании коммитов в правильном формате можно использовать утилиту commitizen:

```bash
# Установка commitizen (опционально)
pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org commitizen

# Создание коммита в формате Conventional Commits
cz commit
```

## Разработка

Если вы хотите внести вклад в развитие проекта или доработать его под свои нужды:

1. Форкните репозиторий
2. Создайте ветку для вашей функциональности
3. Внесите изменения
4. Зафиксируйте изменения, следуя формату [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` для новой функциональности
   - `fix:` для исправления ошибок
   - `docs:` для изменений в документации
   - `style:` для изменений, не влияющих на смысл кода (пробелы, форматирование и т.д.)
   - `refactor:` для рефакторинга кода
   - `perf:` для улучшения производительности
   - `test:` для добавления или изменения тестов
   - `chore:` для изменений в процессе сборки или вспомогательных инструментах
5. Проверьте код с помощью линтера:
   ```bash
   poetry run ruff check .
   ```
6. Запустите тесты:
   ```bash
   poetry run pytest
   ```
7. Соберите пакет:
   ```bash
   poetry build
   ```

## Поддержка и обратная связь

Если у вас возникли проблемы с использованием TiraJira:

1. Проверьте, что все шаги по установке и настройке выполнены корректно
2. Убедитесь, что ваш Jira API доступен и токен действителен
3. Проверьте формат файла с задачами на соответствие примерам

Для получения помощи вы можете:

- Посмотреть логи выполнения в терминале
- Проверить примеры файлов в директории проекта
- Обратиться к документации Jira API по поддерживаемым полям
