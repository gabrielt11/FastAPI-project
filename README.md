### API-сервис сокращения ссылок.
API для укорачивания ссылок на базе FastAPI с JWT-аутентификацией и асинхронной PostgreSQL базой данных. 
Позволяет создавать, обновлять, удалять короткие ссылки, получать статистику и использовать кастомные алиасы.


## Описание API
# Аутентификация
POST /auth/register — регистрация пользователя.
POST /auth/jwt/login — логин, получение JWT токена.

# Работа со ссылками (префикс /links)

# POST /links/shorten
Создание короткой ссылки из оригинального URL.
Требует аутентификации (опционально).
Вход: { "original_url": "https://example.com" }
Выход: объект ссылки с коротким кодом.

# GET /links/search?original_url=...
Поиск ссылки по оригинальному URL.

# GET /links/{short_code}
Редирект на оригинальную ссылку, увеличивает счетчик кликов.

# DELETE /links/{short_code}
Удаление ссылки. Доступно только создателю (требует аутентификации).

# PUT /links/{short_code}
Обновление оригинального URL ссылки. Доступно только создателю.

# GET /links/{short_code}/stats
Получение статистики по ссылке (клики, дата создания, последнее использование).

# POST /links/shorten/custom_alias
Создание короткой ссылки с кастомным алиасом.
Вход: { "original_url": "...", "custom_alias": "myalias" }

# GET /links/list/links
Получение списка всех ссылок текущего пользователя.

# POST /links/pack
Пакетное создание коротких ссылок из списка URL.
Вход: { "original_urls": ["https://site1.com", "https://site2.com"] }

##Инструкция по запуску
#Предварительные требования
Python 3.8+
PostgreSQL (локально или удаленно)
Установите зависимости: pip install fastapi uvicorn sqlalchemy asyncpg fastapi-users[sqlalchemy] python-dotenv
#Шаги
1. Клонируйте репозиторий и перейдите в папку проекта.
2. Создайте файл .env в корне проекта с переменными окружения (см. ниже).
3. Настройте базу данных: Создайте БД и таблицы (используйте models.py для миграций или Alembic, если настроено).
4. Запустите приложение: uvicorn src.main:app --reload
5. Откройте в браузере: http://127.0.0.1:8000/docs (Swagger UI для тестирования API).

#Переменные окружения (.env)
Создайте файл .env в корне проекта:

SECRET=your_jwt_secret_key
DB_USER=your_db_user
DB_PASS=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=url_shortener

## Примеры запросов
# 1. POST /links/shorten — Создание короткой ссылки
Описание: Создаёт короткую ссылку для заданного URL.

Пример запроса:

POST /links/shorten HTTP/1.1
Content-Type: application/json

{
  "original_url": "https://example.com/some/long/url"
}
Ответ:

{
  "id": 1,
  "original_url": "https://example.com/some/long/url",
  "short_link": "a1b2c3",
  "creator_id": null,
  "created_at": "2024-06-01T12:00:00Z",
  "clicks": 0,
  "last_used_at": null
}
# 2. GET /links/search?original_url=... — Поиск ссылки по оригинальному URL
Пример запроса:

GET /links/search?original_url=https://example.com/some/long/url HTTP/1.1
# 3. GET /links/{short_code} — Редирект по короткому коду
Пример запроса:

GET /links/a1b2c3 HTTP/1.1
Ответ: HTTP редирект на оригинальный URL.

# 4. DELETE /links/{short_code} — Удаление ссылки (требуется аутентификация)
Пример запроса:

DELETE /links/a1b2c3 HTTP/1.1
Authorization: Bearer <token>
# 5. PUT /links/{short_code} — Обновление оригинального URL ссылки (требуется аутентификация)
Пример запроса:

PUT /links/a1b2c3 HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{
  "original_url": "https://example.com/new/url"
}
# 6. GET /links/{short_code}/stats — Получение статистики по ссылке
Пример запроса:

GET /links/a1b2c3/stats HTTP/1.1
# 7. POST /links/shorten/custom_alias — Создание короткой ссылки с пользовательским алиасом
Пример запроса:

POST /links/shorten/custom_alias HTTP/1.1
Content-Type: application/json

{
  "original_url": "https://example.com/page",
  "custom_alias": "myalias"
}
# 8. GET /links/list/links — Получение списка ссылок пользователя (требуется аутентификация)
Пример запроса:

GET /links/list/links HTTP/1.1
Authorization: Bearer <token>
# 9. POST /links/pack — Пакетное создание коротких ссылок
Пример запроса:

POST /links/pack HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{
  "original_urls": [
    "https://example.com/page1",
    "https://example.com/page2"
  ]
}


## Описание БД
Проект использует PostgreSQL с SQLAlchemy. Таблицы создаются на основе моделей в models.py.

#Таблицы

# user:

id (Integer, PK)
username (String, not null)
email (String, not null)
hashed_password (String, not null)
registered_at (Timestamp)
is_active (Boolean)
is_superuser (Boolean)
is_verified (Boolean)

# links:

id (Integer, PK)
original_url (String, not null)
short_link (String, unique, not null) — короткий код (6 символов UUID)
created_at (Timestamp)
clicks (Integer, default 0)
last_used_at (Timestamp, nullable)
expires_at (Timestamp, nullable)
creator_id (Integer, FK to user.id, nullable)

# Связи
User.links: Один ко многим с Link (user может иметь много ссылок).

Для настройки подключения используйте переменные из .env. Если нужно, добавьте миграции с Alembic.
