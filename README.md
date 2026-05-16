# Контрольная работа №2 по FastAPI

## Структура проекта

- `main.py` - Основное приложение со всеми заданиями
- `models.py` - Pydantic модели
- `requirements.txt` - Зависимости

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:
```bash
pip install -r requirements.txt
Доступные эндпоинты
Задание 3.1
POST /create_user - Создание пользователя с валидацией

json
{
  "name": "Alice",
  "email": "alice@example.com",
  "age": 30,
  "is_subscribed": true
}
Задание 3.2
GET /product/{product_id} - Получение продукта по ID

GET /products/search?keyword=phone&category=Electronics&limit=5 - Поиск продуктов

Задание 5.1
POST /login - Вход в систему с установкой cookie

json
{
  "username": "user123",
  "password": "password123"
}
GET /user - Получение профиля (требуется cookie session_token)

Задание 5.2
POST /login-signed - Вход с подписанной cookie

json
{
  "username": "user123",
  "password": "password123"
}
GET /profile - Получение профиля с проверкой подписи

Задание 5.3
POST /login-advanced - Вход с динамической сессией

json
{
  "username": "user123",
  "password": "password123"
}
GET /profile-advanced - Профиль с продлением сессии (3-5 мин)

Задание 5.4
GET /headers - Получение User-Agent и Accept-Language

Задание 5.5
GET /headers-v2 - Заголовки через модель CommonHeaders

GET /info - Расширенная информация с заголовком X-Server-Time

Тестовые данные
Пользователь для входа:
json
{
  "username": "user123",
  "password": "password123"
}
Продукты для поиска:
Smartphone (123) - Electronics - $599.99

Phone Case (456) - Accessories - $19.99

Iphone (789) - Electronics - $1299.99

Headphones (101) - Accessories - $99.99

Smartwatch (202) - Electronics - $299.99