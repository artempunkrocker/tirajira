# Настройка подключения к Jira

TiraJira поддерживает два режима аутентификации в зависимости от типа вашего Jira:

| Тип Jira | Режим аутентификации | Переменные среды |
|----------|---------------------|------------------|
| Jira Cloud | Basic Auth | `JIRA_SERVER`, `JIRA_EMAIL`, `JIRA_API_TOKEN` |
| Jira Server/Data Center | Personal Access Token | `JIRA_SERVER`, `JIRA_PAT_TOKEN` |

## Настройка для Jira Cloud

1. Создайте файл `.env` в рабочей директории:
   ```bash
   cp .env.example .env
   ```

2. Откройте `.env` и заполните параметры:
   ```env
   JIRA_SERVER=https://your-company.atlassian.net
   JIRA_EMAIL=your-email@company.com
   JIRA_API_TOKEN=your-api-token-here
   ```

3. Получение API-токена:
   - Перейдите в [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Нажмите "Create API token"
   - Скопируйте токен и вставьте в `.env`

## Настройка для Jira Server/Data Center

1. Создайте файл `.env`:
   ```bash
   cp .env.example .env
   ```

2. Заполните параметры:
   ```env
   JIRA_SERVER=https://your-jira-server.company.com
   JIRA_PAT_TOKEN=your-personal-access-token-here
   ```

3. Получение PAT:
   - В Jira перейдите в "Профиль" → "Personal Access Tokens"
   - Нажмите "Create token"
   - Укажите имя и срок действия
   - Скопируйте токен и вставьте в `.env`

## Приоритет переменных окружения

⚠️ **Важно:** Переменная `JIRA_PAT_TOKEN` имеет приоритет над Basic Auth. Если она указана, будет использоваться PAT.

## Проверка подключения

После настройки переменных окружения вы можете проверить подключение, попытавшись создать одну тестовую задачу с параметром `--verbose`:

```bash
tirajira import test_task.json --verbose
```

## Безопасность

- Не храните учетные данные в коде
- Используйте переменные окружения
- Не коммитьте .env файлы
- Не записывайте токены в логи