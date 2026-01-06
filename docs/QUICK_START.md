# Быстрый старт / Quick Start Guide

##  ВЕБ-ИНТЕРФЕЙС (РЕКОМЕНДУЕТСЯ)

### Запуск веб-интерфейса

```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Запустите Flask API сервер
python api_server.py
```

**Сервер запустится на <http://localhost:5000>**

### Открытие веб-интерфейса

Откройте в браузере один из файлов:

- **`voyage_planner_ru.html`** - планировщик рейсов (русский интерфейс)
- **`vessel_scheduler_enhanced.html`** - расширенный планировщик судов
- **`voyage_planner.html`** - англоязычный интерфейс

### API Endpoints (доступны после запуска server)

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/health` | GET | Проверка работы сервера |
| `/api/vessels` | GET/POST | Получить/обновить данные судов |
| `/api/cargo` | GET/POST | Получить/обновить грузы |
| `/api/schedule/generate` | POST | Сгенерировать расписание |
| `/api/export/gantt` | POST | Экспорт Gantt chart в Excel |
| `/api/export/fleet-overview` | POST | Экспорт обзора флота |
| `/api/upload/csv` | POST | Загрузить CSV файл |
| `/api/dashboard/stats` | GET | Статистика dashboard |

---

##  КОМАНДНАЯ СТРОКА (альтернатива)

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Генерация тестовых данных

Создайте шаблоны CSV файлов для ввода данных:

```bash
python generate_templates.py
```

Будут созданы шаблоны в директории `templates/`:

- `templates/balakovo/` - шаблоны для Балаково
- `templates/olya/` - шаблоны для Olya
- `templates/deepsea/` - шаблоны для Deep Sea

### 3. Запуск основных команд

#### Планирование рейсов Deep Sea

```bash
python main_deepsea.py
```

Создаст график Gantt для океанских рейсов на основе данных из `input/`.

#### Планирование рейсов Olya (река-море)

```bash
python main_olya.py
```

Создаст график координации барж между Балаково и Olya.

#### Планирование погрузки в Балаково

```bash
python main_balakovo.py
```

Оптимизирует использование причалов и график погрузки.

### 4. Проверка работы тестов

```bash
pytest tests/ -v
```

Должно быть: **59 passed** 

---

##  Структура проекта

```
project/
├── modules/              # Основные модули
│   ├── olya_*.py        # Модули для Olya
│   ├── deepsea_*.py     # Модули для Deep Sea
│   └── balakovo_*.py    # Модули для Балаково
├── input/               # Входные CSV файлы
│   ├── Vessels.csv
│   ├── Cargo.csv
│   └── Routes.csv
├── output/              # Выходные Excel файлы
├── tests/               # Тесты
└── main_*.py            # Точки входа
```

---

##  Базовые сценарии использования

### Сценарий 1: Расчёт рейса Deep Sea

**Цель**: Рассчитать время и стоимость рейса океанского судна

**Шаги**:

1. Отредактируйте `input/Vessels.csv` - добавьте судно
2. Отредактируйте `input/Cargo.csv` - добавьте груз
3. Отредактируйте `input/Routes.csv` - укажите маршруты
4. Запустите:

   ```bash
   python main_deepsea.py
   ```

5. Откройте результат: `output/deepsea/gantt_deepsea_2025_01.xlsx`

### Сценарий 2: Координация погрузки в Балаково

**Цель**: Спланировать график работы причалов

**Шаги**:

1. Создайте шаблоны (если ещё не создали):

   ```bash
   python generate_templates.py
   ```

2. Скопируйте шаблоны из `templates/balakovo/` в `input/`:

   ```bash
   # Windows
   copy templates\balakovo\*.csv input\
   
   # Linux/Mac
   cp templates/balakovo/*.csv input/
   ```

3. Отредактируйте файлы в `input/`:
   - `berths_balakovo.csv` - причалы
   - `fleet_balakovo.csv` - флот
   - `cargo_plan_balakovo.csv` - план отгрузок
4. Запустите:

   ```bash
   python main_balakovo.py
   ```

5. Откройте результат: `output/balakovo/schedule_balakovo.xlsx`

### Сценарий 3: Планирование Olya (река-море)

**Цель**: Скоорд инировать перевалку Балаково → Olya → Иран

**Шаги**:

1. Заполните `input/vessels_olya.csv`
2. Заполните `input/cargo_olya.csv`
3. Запустите:

   ```bash
   python main_olya.py
   ```

4. Откройте результат: `output/olya/gantt_olya_2025_01.xlsx`

---

##  Настройка конфигурации

Отредактируйте [`config.yaml`](../config.yaml) для изменения параметров:

```yaml
deepsea:
  default_speed_kts: 14          # Скорость судна по умолчанию
  loading_rate_mt_per_day: 5000  # Норма погрузки

olya:
  default_speed_kph: 15           # Скорость речных судов
  num_berths: 2                   # Количество причалов

balakovo:
  default_load_rate: 2500         # Норма погрузки
  berth_capacity_mt: 10000        # Вместимость причала
```

---

##  Формат входных данных

### CSV файлы

Все CSV файлы используют:

- **Разделитель**: `;` (точка с запятой)
- **Кодировка**: UTF-8
- **Формат дат**: YYYY-MM-DD
- **Комментарии**: строки начинаются с `#`

### Пример: Vessels.csv

```csv
vessel_id;vessel_name;vessel_class;dwt_mt;speed_kts
V001;Atlantic Star;Handysize;35000;14
V002;Pacific Dawn;Panamax;75000;15
```

### Пример: Cargo.csv

```csv
cargo_id;commodity;quantity_mt;load_port;disch_port;laycan_start;laycan_end
C001;Grain;50000;Houston;Rotterdam;2025-01-15;2025-01-20
```

---

##  Выходные файлы

### Gantt Charts

Файлы Excel с графиками Gantt создаются в `output/`:

**Ежемесячные графики**:

- `gantt_deepsea_2025_01.xlsx` - Deep Sea за январь 2025
- `gantt_olya_2025_01.xlsx` - Olya за январь 2025

**Сводные отчёты**:

- `fleet_overview.xlsx` - обзор всего флота
- `utilization_report.xlsx` - статистика использования

### Структура Gantt Chart

| Столбец | Описание |
|---------|----------|
| **Vessel** | Название судна |
| **01-31** | Дни месяца с операциями |
| **Legend** | Легенда операций |
| **Stats** | Статистика |

**Обозначения операций**:

- `L` - Loading (погрузка)
- `D` - Discharge (выгрузка)
- `→` - Sea transit laden (морской переход с грузом)
- `⟶` - Ballast (балласт)
- `C` - Canal (канал)
- `W` - Waiting (ожидание)

---

##  Тестирование

### Запуск всех тестов

```bash
pytest tests/ -v
```

### Запуск конкретного test файла

```bash
pytest tests/test_template_generator.py -v
```

### Запуск с покрытием кода

```bash
pytest tests/ --cov=modules --cov-report=html
```

Откройте `htmlcov/index.html` для просмотра отчёта.

---

##  Устранение проблем

### Проблема: Тесты не запускаются

**Симптом**: `ModuleNotFoundError: No module named 'modules'`

**Решение**:

```bash
# Убедитесь, что запускаете из корневой директории проекта
cd c:/Users/Asus/Documents/project
pytest tests/ -v
```

### Проблема: Не создаются Excel файлы

**Проверьте**:

1. Есть ли CSV файлы в `input/`?
2. Правильный ли формат CSV (разделитель `;`)?
3. UTF-8 кодировка?
4. Права на запись в `output/`?

### Проблема: Ошибка при открытии Excel

**Симптомы**: Excel не может открыть файл

**Решение**:

1. Обновите openpyxl: `pip install --upgrade openpyxl`
2. Проверьте, что в ячейках нет None значений
3. Используйте "Открыть и восстановить" в Excel

---

##  Дополнительные ресурсы

- [`README.md`](../README.md) - Полная документация
- [`tests/README.md`](../tests/README.md) - Документация по тестам
- [`docs/EXCEL_GANTT_FIX.md`](EXCEL_GANTT_FIX.md) - Решение проблем с Excel
- [`.kilocode/rules/rules.md`](../.kilocode/rules/rules.md) - Правила проекта

---

##  Полезные команды

```bash
# Генерация шаблонов
python generate_templates.py

# Запуск Deep Sea планирования
python main_deepsea.py

# Запуск Olya планирования
python main_olya.py

# Запуск Balakovo планирования
python main_balakovo.py

# Запуск всех тестов
pytest tests/ -v

# Проверка версии Python
python --version

# Список установленных пакетов
pip list

# Обновление зависимостей
pip install -r requirements.txt --upgrade
```

---

## ⏱ Типичное время выполнения

| Операция | Время |
|----------|-------|
| Установка зависимостей | ~1-2 мин |
| Генерация шаблонов | <1 сек |
| Расчёт 10 рейсов Deep Sea | ~2-5 сек |
| Планирование 20 операций Olya | ~3-7 сек |
| Оптимизация Балаково (100 грузов) | ~5-10 сек |
| Запуск всех тестов (59 тестов) | ~1 сек |

---

**Последнее обновление**: 2025-12-18  
**Версия**: 1.0.0
