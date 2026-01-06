# Веб-интерфейсы / Web Interfaces

## Обзор

Проект содержит два основных вебинтерфейса с разными функциями:

1. **Vessel Scheduler Enhanced** - Полнофункциональная система планирования
2. **Voyage Planner** - Автономный калькулятор рейсов

---

## 1. Vessel Scheduler Enhanced

**Файл**: [`vessel_scheduler_enhanced.html`](../vessel_scheduler_enhanced.html)  
**JavaScript**: [`vessel_scheduler_enhanced.js`](../vessel_scheduler_enhanced.js)

### Возможности

####  Dashboard

- Статистика в реальном времени
- Активные суда, грузы, маршруты
- Общая дистанция и загрузка флота

####  Управление судами (Vessels)

- Просмотр списка судов
- Добавление/редактирование судов
- Фильтрация по классу, флагу, типу
- Модальные формы для редактирования

####  Управление грузами (Cargo)

- Просмотр грузов
- Создание cargo fixtures
- Laycan dates управление
- Фильтры по commodity, портам

####  Маршруты (Routes)

- Управление маршрутами между портами
- Distances, transit times
- Canal информация

####  Schedule Generation

- Генерация расписания для DeepSea/Olya/Balakovo
- Визуализация графика Gantt
- Легенда операций (Loading, Discharge, Sea, Canal, etc.)

####  Voyage Builder

- Построение рейсов вручную
- Пошаговое добавление legs
- Custom voyage creation

####  Сценарии Сравнения

- Мультисценарный анализ
- Сравнение вариантов расписания
- What-if analysis

####  Port Stock Management

- Складские остатки в портах
- Cargo movements tracking
- Stock level monitoring

####  Sales Plan

- План продаж
- Revenue tracking
- Sales statistics

####  Network Optimization

- Оптимизация сети маршрутов
- Route efficiency analysis

####  Reports & Export

- **Excel Exports**:
  - Gantt Chart
  - Fleet Overview
  - Voyage Summary
  - Utilization Report
  - Cost Analysis
  - Revenue Summary
  - Distance Report
  - Performance Metrics

- **Import CSV**:
  - Vessels data
  - Cargo data
  - Routes
  - Ports
  - VoyagePl ans
  - Berth Capacity
  - Fleet Configuration
  - Cargo Plans

### API Integration

Работает с Flask API ([`api_server.py`](../api_server.py)):

- `GET/POST /api/vessels`
- `GET/POST /api/cargo`
- `POST /api/schedule/generate`
- `POST /api/export/gantt`
- `GET /api/dashboard/stats`

---

## 2. Voyage Planner

**Файлы**:

- [`voyage_planner.html`](../voyage_planner.html) - английская версия
- [`voyage_planner_ru.html`](../voyage_planner_ru.html) - русская версия
- [`voyage-planner-functions.js`](../voyage-planner-functions.js) - общая логика

### Возможности

####  Auto номный калькулятор рейсов

- **Offline mode**: работает без API сервера
- Расчет времени рейса
- Расчет стоимости (TCE)
- Berth constraints учёт

####  Voyage Calculation

- Distance calculation
- Transit time estimation
- Loading/unloading time
- Port waiting time
- Canal transits
- Bunker cost estimation

####  Schedule with Berth Constraints

- Berth capacity management
- Queue system simulation
- Arrival/departure windows
- Demurrage calculation

####  Data Management

- **Import Excel/CSV**:
  - Cargo plans
  - Vessel specifications
  - Port data
  - Berth capacity configurations

- **Export Results**:
  - Excel schedules
  - Gantt charts
  - Summary reports

####  Configuration

- Vessel speeds
- Loading/unloading rates
- Port costs
- Canal fees
- Demurrage rates
- Weather margins

### Отличия от Vessel Scheduler Enhanced

| Характеристика | Vessel Scheduler Enhanced | Voyage Planner |
|----------------|---------------------------|----------------|
| **Работа** | Online (требует API) | Offline (автономный) |
| **Фокус** | Комплексное планирование | Расчёт рейсов |
| **Модули** | Multi-module (Olya/DeepSea/Balakovo) | Single purpose |
| **Интеграция** | Flask API + Database | Browser only (Excel I/O) |
| **Berth Management** | Basic planning | Advanced berth constraints |
| **UI Complexity** | Advanced (9 tabs) | Simple (3 tabs) |
| **Scenario Planning** | Yes | No |
| **Network Optimization** | Yes | No |
| **Sales Planning** | Yes | No |
| **Port Stock** | Yes | No |

---

## Когда использовать что?

### Используйте Vessel Scheduler Enhanced когда

-  Нужно комплексное планирование всех модулей
-  Требуется работа с базой данных через API
-  Нужны сценарии и оптимизация
-  Управление портовыми остатками
-  Планирование продаж
-  Сетевая оптимизация

### Используйте Voyage Planner когда

-  Нужен простой расчёт рейса
-  Работаете без интернета/API
-  Нужен детальный учёт берth constraints
-  Быстрый import/export Excel
-  Не требуется сложная интеграция
-  Фокус на одном рейсе/портовом окне

---

## Запуск

### Vessel Scheduler Enhanced

```bash
# 1. Запустить Flask API
python api_server.py

# 2. Открыть браузер
# http://localhost:5000/vessel_scheduler_enhanced.html
```

### Voyage Planner

```bash
# Просто открыть в браузере (без API)
# file:///path/to/voyage_planner.html

# ИЛИ через Flask server
python api_server.py
# http://localhost:5000/voyage_planner.html
```

---

## Совместное использование

Оба интерфейса могут работать параллельно:

1. **Vessel Scheduler** для стратегического планирования
2. **Voyage Planner** для тактических расчётов отдельных рейсов

**Рабочий процесс**:

1. Импортируйте флота vessel_scheduler_enhanced.html
2. Создайте сценарии и расписание
3. Экспортируйте отдельные рейсы в Excel
4. Используйте voyage_planner.html для детального расчёта constraints
5. Вернитесь в vessel_scheduler для финальной оптимизации

---

**Последнее обновление**: 2025-12-18  
**Версия**: 1.1.0
