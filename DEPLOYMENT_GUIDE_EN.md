# Production Deployment Guide

**Version:** 2.0.0  
**Last Updated:** January 2026

## 1. Introduction

This guide outlines the procedures for deploying the Vessel Scheduler application to a production environment. It covers build processes, server configuration, security hardening, and maintenance protocols.

## 2. Pre-Deployment Checklist

Before initiating deployment, ensure the following criteria are met:

### 2.1 Code Quality
*   All automated tests pass (`npm run test:all`, `pytest`).
*   Static analysis reveals no critical issues (`npm run lint`, `npm run type-check`).
*   Security audit is clean (`npm audit`).

### 2.2 Configuration
*   Production environment variables are defined.
*   Database connection strings are verified.
*   Logging levels are set to `INFO` or `ERROR`.

### 2.3 Security
*   SSL/TLS certificates are ready.
*   Firewall rules are configured.
*   Secrets are securely managed (not committed to version control).

## 3. Build Process

### 3.1 Frontend Build

Generate the optimized static assets for the Vue.js application.

```bash
npm run build
```

**Output**: The build artifacts will be located in the `dist/` directory.

### 3.2 Backend Preparation

Ensure all Python dependencies are locked and compatible.

```bash
pip freeze > requirements.txt
```

## 4. Environment Configuration

### 4.1 Frontend Variables (`.env.production`)

Create a `.env.production` file in the project root:

```ini
VITE_API_URL=https://api.yourdomain.com
VITE_APP_ENV=production
```

### 4.2 Backend Variables (`.env`)

Create a `.env` file for the Flask server:

```ini
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
HOST=0.0.0.0
PORT=5000
CORS_ORIGINS=https://yourdomain.com
```

## 5. Deployment Options

### 5.1 Option 1: Traditional Server (NGINX + Gunicorn)

**Architecture**: NGINX serves static files and reverse proxies API requests to Gunicorn.

1.  **Transfer Files**: Copy `dist/`, `modules/`, `*.py`, and `requirements.txt` to the server.
2.  **Install Dependencies**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt gunicorn
    ```
3.  **Configure Systemd Service**:
    Create `/etc/systemd/system/vessel-scheduler.service`:
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
4.  **Configure NGINX**:
    Set up a server block to serve `dist/` at `/` and proxy `/api` to `127.0.0.1:5000`.

### 5.2 Option 2: Docker Containerization

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

**Deployment**:
```bash
docker build -t vessel-scheduler .
docker run -d -p 5000:5000 --env-file .env vessel-scheduler
```

## 6. Server Configuration

### 6.1 NGINX Security Headers

Add the following headers to the NGINX configuration to enhance security:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 6.2 SSL Configuration

Use Certbot to obtain and install Let's Encrypt certificates:

```bash
sudo certbot --nginx -d yourdomain.com
```

## 7. Monitoring and Maintenance

### 7.1 Logging

*   **Application Logs**: Configured to write to `logs/app.log`.
*   **Access Logs**: NGINX access logs at `/var/log/nginx/access.log`.
*   **Error Logs**: NGINX error logs at `/var/log/nginx/error.log`.

### 7.2 Backup Strategy

Implement a daily backup routine for data files:

```bash
#!/bin/bash
tar -czf /backups/app_$(date +%Y%m%d).tar.gz /opt/vessel-scheduler/input /opt/vessel-scheduler/output
```

### 7.3 Updates

To update the application:
1.  Pull the latest code.
2.  Rebuild the frontend (`npm run build`).
3.  Update Python dependencies (`pip install -r requirements.txt`).
4.  Restart the service (`sudo systemctl restart vessel-scheduler`).

## 8. Troubleshooting

*   **502 Bad Gateway**: Indicates Gunicorn is not running. Check systemd status.
*   **Static Files Not Found**: Verify NGINX root path matches the `dist/` directory location.
*   **CORS Errors**: Ensure `CORS_ORIGINS` in `.env` matches the frontend domain.
