![workflow](https://github.com/find-frend/find_friend_backend/actions/workflows/find_friend_workflow.yml/badge.svg)

# Бэкенд приложения "Найди друга"

Знакомства с новыми людьми, поиск людей с общими интересами и организация совместных мероприятий

## Структура проекта:

| Имя   | Описание                                                  |
| ----- | --------------------------------------------------------- |
| src   | Файлы для backend разработки                              |
| infra | Docker-compose файлы для запуска проекта с помощью Docker |

## Подключенные приложения:

1. Users - отвечает за создание пользователей
2. Api - вспомогательное приложение для api

## Правила работы с git (как делать коммиты и pull request-ы):

1. Две основные ветки: `main` и `develop`
2. Ветка `develop` — “предрелизная”. Т.е. здесь должен быть рабочий и выверенный код
3. В `main` находится только production-ready код (CI/CD)
4. Создавая новую ветку, наследуйтесь от ветки `develop`
5. Правила именования веток
   - весь новый функционал — `feature/название-функционала`
   - исправление ошибок — `bugfix/название-багфикса`
6. Пушим свою ветку в репозиторий и открываем Pull Request

## Добавление пакетов в requireremens.txt

При установке пакетов не забывайте добавлять их в requirements.txt!
Если устанавливаемый вами пакет нужен только на этапе разработки и не требуеся на боевом сервере, прописывайте зависимость в requirements-**dev**.txt!

## Запуск приложения:

**!!! ИНСТРУКЦИЯ ДЛЯ ЭТАПА РАЗРАБОТКИ !!!**

Для локальной разработки нужно:

1. Клонировать репозиторий и перейти в директорию:

```
git clone git@github.com:find-frend/find_friend_backend.git
```

```
cd find_friend_backend/
```

2. Создать и активировать виртуальное окружение:

```
python -m venv venv                      # Устанавливаем виртуальное окружение
source venv/scripts/activate             # Активируем (Windows); или
source venv/bin/activate                 # Активируем (Linux)
python -m pip install --upgrade pip      # Обновляем менеджер пакетов pip
pip install -r src/requirements-dev.txt  # Устанавливаем пакеты для разработки
```

3. Установить пре-коммит хуки:

```
pre-commit install
```

4. Создать файл `.env` с переменными окружения из `.env.example`. Пример наполнения - непосредственно в `.env.example`. Значение DEBUG при локальной разработке (в т.ч. для запуска дев сервера через python manage.py runserver) должно быть `True.`Для локальной разработки параметры DB не нужны, т.к. используется SQLite. Параметр `DJANGO_ALLOWED_HOSTS` можно закомментировать. Вот как выглядит `.env` для разработки:

```
DEBUG=True
DJANGO_SECRET_KEY=somegeneratedsecretkey
```

---

Для запуска приложения в контейнерах необходимо:

1. Заполнить `.env`:

```
DEBUG=False

DJANGO_SECRET_KEY=somegeneratedsecretkey

# Выставляем так, как ниже
DJANGO_ALLOWED_HOSTS=127.0.0.1 localhost backend 158.160.60.2

DB_ENGINE=django.db.backends.postgresql_psycopg2
POSTGRES_DB=findafriend
POSTGRES_USER=postgresusername
POSTGRES_PASSWORD=postgresuserpassword
DB_HOST=db
DB_PORT=5432
```

2. Перейти в директорию с файлом _docker-compose.dev.yaml_, открыть терминал и запустить docker-compose с ключом `-d`:

```
cd infra/dev/
```

```
docker compose -f docker-compose.dev.yaml up -d
```

3. Выполнить миграции:

```
docker compose -f docker-compose.dev.yaml exec backend python manage.py migrate
```

4. Создать суперюзера:

```
docker compose -f docker-compose.dev.yaml exec backend python manage.py createsuperuser
```

5. Собрать статику:

```
docker compose -f docker-compose.dev.yaml exec backend python manage.py collectstatic --no-input
```

6. После успешного запуска проект станет доступен по адресу:
   http://localhost/api - Корень api
   http://localhost/admin - Админка Django

7. Остановить проект:

```
docker compose -f docker-compose.dev.yaml down
```

8. Если необходимо пересобрать контейнеры после изменений в проекте:

```
docker compose -f docker-compose.dev.yaml up -d --build
```

## Регистрация и авторизация пользователей

Авторизация реализована с помощью токенов: пользователь регистрируется с емейлом и паролем, отдельным запросом получает токен, затем этот токен передаётся в заголовке каждого запроса.

Уровни доступа пользователей:

- Гость (неавторизованный пользователь)
- Авторизованный пользователь
- Администратор

Что могут делать неавторизованные пользователи
- Создать аккаунт.
  Что могут делать авторизованные пользователи
- Входить в систему под своим логином и паролем.
- Выходить из системы (разлогиниваться).
- Менять свой пароль.

Что может делать администратор
Администратор обладает всеми правами авторизованного пользователя.
Плюс к этому он может:
- изменять пароль любого пользователя,
- создавать/блокировать/удалять аккаунты пользователей,

Эти функции реализованы в стандартной админ-панели Django.

_*Спецификации API в файле `openapi-schema.yml` в папке `docs`*_

Также документация API доступна по адресам:

- JSON - `/swagger.json`
- YAML - `/swagger.yaml`
- Swagger UI - `/swagger/`
- ReDoc UI - `/redoc/`
