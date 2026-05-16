from fastapi import FastAPI, HTTPException, Request, Response, Header, Depends, Cookie
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import uuid
import time
from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired
from datetime import datetime, timedelta

from models import UserCreate, LoginRequest, CommonHeaders

app = FastAPI(title="Контрольная работа №2")

# ===== Данные для заданий =====

# Тестовые пользователи
USERS_DB = {
    "user123": {
        "id": "user123",
        "username": "user123",
        "password": "password123",
        "name": "John Doe",
        "email": "john@example.com"
    }
}

# Тестовые продукты (Задание 3.2)
sample_product_1 = {
    "product_id": 123,
    "name": "Smartphone",
    "category": "Electronics",
    "price": 599.99
}

sample_product_2 = {
    "product_id": 456,
    "name": "Phone Case",
    "category": "Accessories",
    "price": 19.99
}

sample_product_3 = {
    "product_id": 789,
    "name": "Iphone",
    "category": "Electronics",
    "price": 1299.99
}

sample_product_4 = {
    "product_id": 101,
    "name": "Headphones",
    "category": "Accessories",
    "price": 99.99
}

sample_product_5 = {
    "product_id": 202,
    "name": "Smartwatch",
    "category": "Electronics",
    "price": 299.99
}

sample_products = [sample_product_1, sample_product_2, sample_product_3, sample_product_4, sample_product_5]

# Секретный ключ для подписи
SECRET_KEY = "your-secret-key-change-in-production"
serializer = URLSafeSerializer(SECRET_KEY)

# Хранилище сессий
sessions = {}


# ===== Задание 3.1: Создание пользователя =====
@app.post("/create_user")
async def create_user(user: UserCreate):
    """
    Создание нового пользователя с валидацией данных
    """
    return {
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "is_subscribed": user.is_subscribed
    }


# ===== Задание 3.2: Продукты =====
@app.get("/product/{product_id}")
async def get_product(product_id: int):
    """
    Получение информации о продукте по ID
    """
    for product in sample_products:
        if product["product_id"] == product_id:
            return product
    
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/products/search")
async def search_products(
    keyword: str,
    category: Optional[str] = None,
    limit: Optional[int] = 10
):
    """
    Поиск продуктов по ключевому слову и категории
    """
    results = []
    
    for product in sample_products:
        if keyword.lower() in product["name"].lower():
            if category is None or product["category"].lower() == category.lower():
                results.append(product)
    
    return results[:limit]


# ===== Задание 5.1: Аутентификация через cookie =====
@app.post("/login")
async def login(login_data: LoginRequest, response: Response):
    """
    Вход в систему с установкой cookie
    """
    user = USERS_DB.get(login_data.username)
    
    if not user or user["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Создаем уникальный токен сессии
    session_token = str(uuid.uuid4())
    
    # Сохраняем сессию
    sessions[session_token] = {
        "user_id": user["id"],
        "username": user["username"],
        "created_at": datetime.now()
    }
    
    # Устанавливаем cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=3600,  # 1 час
        secure=False  # Для тестирования
    )
    
    return {"message": "Login successful", "username": user["username"]}


@app.get("/user")
async def get_user_profile(session_token: Optional[str] = Cookie(None)):
    """
    Получение профиля пользователя по cookie
    """
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    session = sessions.get(session_token)
    if not session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user = USERS_DB.get(session["username"])
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return {
        "id": user["id"],
        "username": user["username"],
        "name": user["name"],
        "email": user["email"]
    }


# ===== Задание 5.2: Подписанные cookie =====
@app.post("/login-signed")
async def login_signed(login_data: LoginRequest, response: Response):
    """
    Вход в систему с подписанной cookie
    """
    user = USERS_DB.get(login_data.username)
    
    if not user or user["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Создаем подписанный токен
    user_id = user["id"]
    session_token = serializer.dumps(user_id)
    
    # Устанавливаем cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=3600,
        secure=False
    )
    
    return {"message": "Login successful", "username": user["username"]}


@app.get("/profile")
async def get_profile(session_token: Optional[str] = Cookie(None)):
    """
    Получение профиля через подписанную cookie
    """
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        # Проверяем подпись
        user_id = serializer.loads(session_token)
        
        user = USERS_DB.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        return {
            "id": user["id"],
            "username": user["username"],
            "name": user["name"],
            "email": user["email"]
        }
    
    except BadSignature:
        raise HTTPException(status_code=401, detail="Unauthorized")


# ===== Задание 5.3: Динамические сессии =====
def create_session_token(user_id: str, last_activity: float) -> str:
    """
    Создание подписанного токена сессии с временной меткой
    """
    data = f"{user_id}.{last_activity}"
    signature = serializer.dumps(data)
    return f"{user_id}.{last_activity}.{signature}"


def verify_session_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Проверка токена сессии
    """
    try:
        # Разбиваем токен на части
        parts = token.split(".", 2)
        if len(parts) != 3:
            return None
        
        user_id, timestamp_str, signature = parts
        
        # Проверяем подпись
        data = f"{user_id}.{timestamp_str}"
        try:
            serializer.loads(signature)
        except BadSignature:
            return None
        
        last_activity = float(timestamp_str)
        current_time = time.time()
        
        # Проверяем, не истекла ли сессия (5 минут)
        if current_time - last_activity > 300:  # 5 минут
            return None
        
        return {
            "user_id": user_id,
            "last_activity": last_activity,
            "is_valid": True
        }
    
    except (ValueError, TypeError):
        return None


@app.post("/login-advanced")
async def login_advanced(login_data: LoginRequest, response: Response):
    """
    Расширенный вход с динамической сессией
    """
    user = USERS_DB.get(login_data.username)
    
    if not user or user["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    current_time = time.time()
    
    # Создаем токен с временной меткой
    token = create_session_token(user["id"], current_time)
    
    # Сохраняем сессию
    sessions[token] = {
        "user_id": user["id"],
        "username": user["username"],
        "last_activity": current_time
    }
    
    # Устанавливаем cookie
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        max_age=300,  # 5 минут
        secure=False
    )
    
    return {"message": "Login successful", "username": user["username"]}


@app.get("/profile-advanced")
async def get_profile_advanced(
    request: Request,
    response: Response,
    session_token: Optional[str] = Cookie(None)
):
    """
    Получение профиля с динамическим управлением сессией
    """
    if not session_token:
        response.status_code = 401
        return {"message": "Unauthorized"}
    
    # Проверяем токен
    session_data = verify_session_token(session_token)
    if not session_data:
        response.status_code = 401
        return {"message": "Session expired"}
    
    user = USERS_DB.get(session_data["user_id"])
    if not user:
        response.status_code = 401
        return {"message": "Invalid session"}
    
    current_time = time.time()
    last_activity = session_data["last_activity"]
    time_diff = current_time - last_activity
    
    # Проверяем, нужно ли обновить сессию
    if time_diff >= 180 and time_diff < 300:  # От 3 до 5 минут
        # Продлеваем сессию
        new_token = create_session_token(user["id"], current_time)
        
        # Обновляем cookie
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            max_age=300,
            secure=False
        )
        
        # Обновляем данные сессии
        sessions.pop(session_token, None)
        sessions[new_token] = {
            "user_id": user["id"],
            "username": user["username"],
            "last_activity": current_time
        }
    
    return {
        "id": user["id"],
        "username": user["username"],
        "name": user["name"],
        "email": user["email"]
    }


# ===== Задание 5.4: Заголовки запроса =====
@app.get("/headers")
async def get_headers(request: Request):
    """
    Получение заголовков запроса
    """
    user_agent = request.headers.get("User-Agent")
    accept_language = request.headers.get("Accept-Language")
    
    if not user_agent or not accept_language:
        raise HTTPException(status_code=400, detail="Missing required headers")
    
    # Опциональная проверка формата Accept-Language
    accept_lang_pattern = r'^[a-zA-Z]{2,3}(-[a-zA-Z]{2,})?(,\s*[a-zA-Z]{2,3}(-[a-zA-Z]{2,})?(;\s*q=\d(\.\d)?)?)*$'
    if not re.match(accept_lang_pattern, accept_language):
        raise HTTPException(status_code=400, detail="Invalid Accept-Language format")
    
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }


# ===== Задание 5.5: Модель заголовков =====
import re

@app.get("/headers-v2")
async def get_headers_v2(headers: CommonHeaders = Depends()):
    """
    Получение заголовков с использованием модели
    """
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }


@app.get("/info")
async def get_info(headers: CommonHeaders = Depends(), response: Response = None):
    """
    Расширенная информация с заголовками
    """
    # Добавляем заголовок с серверным временем
    server_time = datetime.now().isoformat()
    response.headers["X-Server-Time"] = server_time
    
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }


# Корневой маршрут для проверки работы
@app.get("/")
async def root():
    return {"message": "Контрольная работа №2 - FastAPI приложение работает!"}