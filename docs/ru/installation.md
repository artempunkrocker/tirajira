# Установка и настройка TiraJira

## Системные требования

- Python 3.10 или выше
- Доступ к Jira Server
- API-токен для доступа к Jira

## Установка для обычных пользователей

Для большинства пользователей рекомендуется установка через pip:

```bash
# Установите TiraJira через pip
pip3 install tirajira

# Проверьте установку
tirajira --version
```

## Установка для разработчиков

Если вы хотите внести вклад в развитие проекта:

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/ваш-логин/tirajira.git
cd tirajira

# 2. Установите зависимости через Poetry
poetry install

# 3. Активируйте виртуальное окружение
poetry shell

# 4. Проверьте установку
tirajira --version
```

Для работы потребуется Python 3.10+ и Poetry. Установите Poetry согласно [официальной документации](https://python-poetry.org/docs/#installation).

## Сборка из исходного кода

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

## Проверка установки

После установки вы сможете использовать утилиту из командной строки:

```bash
# Проверка версии
tirajira --version

# Получение справки
tirajira --help

# Проверка доступных команд
tirajira import --help
tirajira resume --help
tirajira extract-failed --help
```