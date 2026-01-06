# Руководство по развертыванию в продакшн

**Версия:** 2.0.0  
**Дата обновления:** Январь 2026

## 1. Введение

В этом руководстве описаны процедуры развертывания системы планирования судов (Vessel Scheduler) в производственной среде (продакшн). Оно охватывает процессы сборки, конфигурацию сервера, усиление безопасности и протоколы обслуживания.

## 2. Контрольный список перед развертыванием

Перед началом развертывания убедитесь, что выполнены следующие критерии:

### 2.1 Качество кода
*   Все автоматические тесты пройдены (`npm run test:all`, `pytest`).
*   Статический анализ не выявил критических проблем (`npm run lint`, `npm run type-check`).
*   Аудит безопасности чист (`npm audit`).

### 2.2 Конфигурация
*   Определены переменные окружения для продакшена.
*   Строки подключения к базе данных проверены.
*   Уровни логирования установлены на `INFO` или `ERROR`.

### 2.3 Безопасность
*   SSL/TLS сертификаты готовы.
*   Правила брандмауэра настроены.
*   Секреты надежно управляются (не закоммичены в систему контроля версий).

## 3. Процесс сборки

### 3.1 Сборка фронтенда

Сгенерируйте оптимизированные статические ресурсы для приложения Vue.js.

```bash
npm run build
```

**Результат**: Артефакты сборки будут находиться в каталоге `dist/`.

### 3.2 Подготовка бэкенда

Убедитесь, что все зависимости Python зафиксированы и совместимы.

```bash
pip freeze > requirements.txt
```

## 4. Настройка окружения

### 4.1 Переменные фронтенда (`.env.production`)

Создайте файл `.env.production` в корне проекта:

```ini
VITE_API_URL=https://api.yourdomain.com
VITE_APP_ENV=production
```

### 4.2 Переменные бэкенда (`.env`)

Создайте файл `.env` для сервера Flask:

```ini
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
HOST=0.0.0.0
PORT=5000
CORS_ORIGINS=https://yourdomain.com
```

## 5. Варианты развертывания

### 5.1 Вариант 1: Традиционный сервер (NGINX + Gunicorn)

**Архитектура**: NGINX обслуживает статические файлы и проксирует API-запросы к Gunicorn.

1.  **Передача файлов**: Скопируйте `dist/`, `modules/`, `*.py` и `requirements.txt` на сервер.
2.  **Установка зависимостей**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt gunicorn
    ```
3.  **Настройка службы Systemd**:
    Создайте `/etc/systemd/system/vessel-scheduler.service`:
    ```ini
    [Unit]
    Description=Vessel Scheduler API
    After=network.target

    [Service]
    User=www-data
    WorkingDirectory=/opt/vessel-scheduler
    ExecStart=/opt/vessel-scheduler/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 api_server_enhanced:app
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
4.  **Настройка NGINX**:
    Настройте блок сервера для обслуживания `dist/` по адресу `/` и проксирования `/api` на `127.0.0.1:5000`.

### 5.2 Вариант 2: Контейнеризация Docker

**Dockerfile**:

```dockerfile
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY modules/ ./modules/
COPY *.py ./
COPY --from=builder /app/dist ./dist
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api_server_enhanced:app"]
```

**Развертывание**:
```bash
docker build -t vessel-scheduler .
docker run -d -p 5000:5000 --env-file .env vessel-scheduler
```

## 6. Конфигурация сервера

### 6.1 Заголовки безопасности NGINX

Добавьте следующие заголовки в конфигурацию NGINX для повышения безопасности:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 6.2 Конфигурация SSL

Используйте Certbot для получения и установки сертификатов Let's Encrypt:

```bash
sudo certbot --nginx -d yourdomain.com
```

## 7. Мониторинг и обслуживание

### 7.1 Логирование

*   **Логи приложения**: Настроены на запись в `logs/app.log`.
*   **Логи доступа**: Логи доступа NGINX в `/var/log/nginx/access.log`.
*   **Логи ошибок**: Логи ошибок NGINX в `/var/log/nginx/error.log`.

### 7.2 Стратегия резервного копирования

Реализуйте ежедневную процедуру резервного копирования файлов данных:

```bash
#!/bin/bash
tar -czf /backups/app_$(date +%Y%m%d).tar.gz /opt/vessel-scheduler/input /opt/vessel-scheduler/output
```

### 7.3 Обновления

Для обновления приложения:
1.  Получите последний код (pull).
2.  Пересоберите фронтенд (`npm run build`).
3.  Обновите зависимости Python (`pip install -r requirements.txt`).
4.  Перезапустите службу (`sudo systemctl restart vessel-scheduler`).

## 8. Устранение неполадок

*   **502 Bad Gateway**: Указывает на то, что Gunicorn не работает. Проверьте статус systemd.
*   **Static Files Not Found**: Убедитесь, что корневой путь NGINX соответствует расположению каталога `dist/`.
*   **CORS Errors**: Убедитесь, что `CORS_ORIGINS` в `.env` соответствует домену фронтенда.
