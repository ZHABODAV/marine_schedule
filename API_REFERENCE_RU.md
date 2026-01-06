# Справочник API

**Версия:** 2.0.0  
**Дата обновления:** Январь 2026  
**Базовый URL:** `http://localhost:5000`

## 1. Введение

Этот документ представляет собой полный справочник по REST API системы планирования судов (Vessel Scheduler System).

## 2. Аутентификация

Все эндпоинты, за исключением `/api/health` и `/api/auth/login`, требуют аутентификации с использованием Bearer-токена.

### 2.1 Вход в систему (Login)

**Эндпоинт**: `POST /api/auth/login`

**Тело запроса**:
```json
{
    "username": "string",
    "password": "string"
}
```

**Ответ (200 OK)**:
```json
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "username": "admin",
        "role": "Administrator"
    },
    "expires_in": 28800
}
```

### 2.2 Выход из системы (Logout)

**Эндпоинт**: `POST /api/auth/logout`  
**Заголовки**: `Authorization: Bearer {token}`

**Ответ (200 OK)**:
```json
{
    "success": true,
    "message": "Logged out successfully"
}
```

## 3. Статус системы

### 3.1 Проверка работоспособности (Health Check)

**Эндпоинт**: `GET /api/health`  
**Аутентификация**: Не требуется

**Ответ (200 OK)**:
```json
{
    "status": "healthy",
    "version": "2.0.0",
    "services": {
        "database": "ok",
        "api": "ok"
    }
}
```

## 4. Управление судами

### 4.1 Получить список всех судов

**Эндпоинт**: `GET /api/vessels`  
**Заголовки**: `Authorization: Bearer {token}`  
**Параметры запроса**:
*   `module` (необязательно): Фильтр по модулю (`deepsea`, `olya`, `balakovo`)
*   `status` (необязательно): Фильтр по статусу (`active`, `inactive`)

**Ответ (200 OK)**:
```json
{
    "vessels": [
        {
            "vessel_id": "V001",
            "vessel_name": "Atlantic Star",
            "dwt_mt": 35000,
            "status": "active"
        }
    ],
    "count": 1
}
```

### 4.2 Создать судно

**Эндпоинт**: `POST /api/vessels`  
**Заголовки**: `Authorization: Bearer {token}`

**Тело запроса**:
```json
{
    "vessel_id": "V002",
    "vessel_name": "Pacific Dawn",
    "type": "Dry Bulk",
    "dwt_mt": 75000,
    "speed_kts": 15.0,
    "module": "deepsea"
}
```

**Ответ (201 Created)**:
```json
{
    "success": true,
    "vessel_id": "V002",
    "message": "Vessel created successfully"
}
```

## 5. Управление грузами

### 5.1 Получить список всех грузов

**Эндпоинт**: `GET /api/cargo`  
**Заголовки**: `Authorization: Bearer {token}`

**Ответ (200 OK)**:
```json
{
    "cargo": [
        {
            "cargo_id": "C001",
            "commodity": "Grain",
            "quantity_mt": 50000,
            "load_port": "Houston",
            "disch_port": "Rotterdam",
            "status": "pending"
        }
    ]
}
```

### 5.2 Создать груз

**Эндпоинт**: `POST /api/cargo`  
**Заголовки**: `Authorization: Bearer {token}`

**Тело запроса**:
```json
{
    "cargo_id": "C002",
    "commodity": "Wheat",
    "quantity_mt": 60000,
    "load_port": "Buenos Aires",
    "disch_port": "Rotterdam",
    "laycan_start": "2025-02-01",
    "laycan_end": "2025-02-05"
}
```

## 6. Расписание и планирование

### 6.1 Сформировать расписание

**Эндпоинт**: `POST /api/schedule/generate`  
**Заголовки**: `Authorization: Bearer {token}`

**Тело запроса**:
```json
{
    "type": "deepsea",
    "start_date": "2025-01-01",
    "end_date": "2025-01-31",
    "options": {
        "optimize_ballast": true
    }
}
```

**Ответ (200 OK)**:
```json
{
    "success": true,
    "schedule_id": "SCH001",
    "voyages": 15,
    "utilization_pct": 87.5
}
```

### 6.2 Получить расписание

**Эндпоинт**: `GET /api/schedule/{type}`  
**Параметры пути**: `type` (`deepsea`, `olya`, `balakovo`)

**Ответ (200 OK)**:
```json
{
    "schedule_type": "deepsea",
    "period": "2025-01",
    "voyages": []
}
```

### 6.3 Рассчитать рейс

**Эндпоинт**: `POST /api/voyage/calculate`  
**Заголовки**: `Authorization: Bearer {token}`

**Тело запроса**:
```json
{
    "vessel_id": "V001",
    "cargo_id": "C001",
    "route": ["Houston", "Rotterdam"]
}
```

**Ответ (200 OK)**:
```json
{
    "voyage_id": "calculated_001",
    "total_distance_nm": 4800,
    "total_duration_days": 18.5,
    "costs": {
        "total_usd": 452500
    }
}
```

## 7. События календаря

### 7.1 Получить события календаря

**Эндпоинт**: `GET /api/calendar/events`  
**Заголовки**: `Authorization: Bearer {token}`

**Параметры запроса**:
*   `module`: Фильтр по модулю (`olya`, `balakovo`, `deepsea`, `all`). По умолчанию: `all`
*   `vessel`: Фильтр по ID судна.
*   `start_date`: Дата в формате ISO 8601.
*   `end_date`: Дата в формате ISO 8601.

**Ответ (200 OK)**:
```json
{
    "events": [
        {
            "id": "deepsea_V001_1",
            "title": "OCEAN PIONEER - Loading",
            "start": "2025-01-15T08:00:00",
            "end": "2025-01-17T20:00:00",
            "type": "Loading"
        }
    ]
}
```

## 8. Отчеты и экспорт

### 8.1 Экспорт диаграммы Ганта

**Эндпоинт**: `POST /api/export/gantt`  
**Заголовки**: `Authorization: Bearer {token}`

**Тело запроса**:
```json
{
    "type": "deepsea",
    "month": 1,
    "year": 2025,
    "format": "xlsx"
}
```

**Ответ**: Бинарный файл Excel.

### 8.2 Генерация PDF отчета

**Эндпоинт**: `POST /api/reports/pdf/vessel-schedule`  
**Заголовки**: `Authorization: Bearer {token}`

**Тело запроса**:
```json
{
    "type": "deepsea",
    "month": 1,
    "year": 2025
}
```

**Ответ**: Бинарный файл PDF.

## 9. Обработка ошибок

API использует стандартные коды состояния HTTP для указания успеха или неудачи запроса.

| Код | Описание |
|-----|----------|
| 200 | OK - Запрос выполнен успешно |
| 201 | Created - Ресурс успешно создан |
| 400 | Bad Request - Неверные параметры |
| 401 | Unauthorized - Неверный или отсутствующий токен |
| 403 | Forbidden - Недостаточно прав |
| 404 | Not Found - Ресурс не найден |
| 500 | Internal Server Error - Ошибка сервера |

**Формат ответа об ошибке**:
```json
{
    "error": "Описание сообщения об ошибке",
    "code": "ERROR_CODE",
    "timestamp": "2025-12-18T10:30:00Z"
}
```

## 10. Ограничение частоты запросов (Rate Limiting)

Для обеспечения стабильности системы применяются следующие ограничения:

*   **Анонимные запросы**: 100 запросов в час
*   **Аутентифицированные запросы**: 1000 запросов в час
*   **Загрузка файлов**: 20 запросов в час

Статус ограничения передается в заголовках ответа:
*   `X-RateLimit-Limit`
*   `X-RateLimit-Remaining`
*   `X-RateLimit-Reset`
