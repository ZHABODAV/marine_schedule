# Production Deployment Guide

Complete guide for deploying the Vessel Scheduler application to production.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Build Process](#build-process)
3. [Environment Configuration](#environment-configuration)
4. [Deployment Options](#deployment-options)
5. [Server Configuration](#server-configuration)
6. [Performance Optimization](#performance-optimization)
7. [Security Hardening](#security-hardening)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Code Quality

- [ ] All tests passing (`npm run test:all`)
- [ ] No TypeScript errors (`npm run type-check`)
- [ ] ESLint clean (`npm run lint`)
- [ ] Security audit passed (`npm audit`)
- [ ] Python tests passing (`pytest`)

### Documentation

- [ ] API documentation up to date
- [ ] User guide updated
- [ ] Changelog maintained
- [ ] README reflects current version

### Configuration

- [ ] Production environment variables set
- [ ] Database connections configured
- [ ] API endpoints updated
- [ ] Logging levels appropriate
- [ ] Error tracking configured

### Performance

- [ ] Bundle size optimized
- [ ] Images compressed
- [ ] Lazy loading implemented
- [ ] Caching strategies configured
- [ ] CDN configured (if applicable)

### Security

- [ ] HTTPS enabled
- [ ] CORS configured correctly
- [ ] Input validation in place  
- [ ] Authentication implemented
- [ ] Dependencies updated
- [ ] Secrets not in code

---

## Build Process

### Frontend Build

**Development Build:**
```bash
npm run build
```

**Production Build with Analysis:**
```bash
npm run build:analyze
```

**Build Output:**
```
dist/
├── index.html
├── assets/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── fonts/
├── manifest.json
└── sw.js (Service Worker)
```

**Build Configuration:**

The [`vite.config.ts`](../vite.config.ts) includes:

- **Code Splitting:** Vendor chunks separated by library
- **Minification:** Terser with console removal
- **Source Maps:** Enabled for debugging
- **PWA:** Service worker for offline support
- **Asset Optimization:** Images, fonts, CSS optimized
- **Chunk Size Limit:** 500KB warning threshold

**Build Verification:**

```bash
# Preview production build locally
npm run preview

# Check bundle sizes
npm run build:analyze
```

### Backend Build

No build step required for Python, but ensure:

```bash
# Create requirements lock file
pip freeze > requirements.txt

# Verify all dependencies install
pip install -r requirements.txt --no-cache-dir
```

---

## Environment Configuration

### Environment Variables

#### Frontend (.env.production)

Create `.env.production` in project root:

```bash
# API Configuration
VITE_API_URL=https://api.yourdomain.com
VITE_API_TIMEOUT=30000

# App Configuration
VITE_APP_ENV=production
VITE_APP_NAME="Vessel Scheduler"
VITE_APP_VERSION=2.0.0

# Feature Flags
VITE_ENABLE_PWA=true
VITE_ENABLE_ANALYTICS=true

# Logging
VITE_LOG_LEVEL=error
```

#### Backend (Python)

Create `.env` for Python:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DEBUG=False

# Server
HOST=0.0.0.0
PORT=5000

# Database (if applicable)
DATABASE_URL=postgresql://user:pass@localhost/vessel_scheduler

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# CORS
CORS_ORIGINS=https://yourdomain.com
```

**Security Note:** Never commit `.env` files! Add to `.gitignore`.

---

## Deployment Options

### Option 1: Traditional Server Deployment

**Architecture:**
```
[NGINX] → [Flask API:5000] + [Static Files]
```

**Steps:**

1. **Build Frontend:**
   ```bash
   npm run build
   ```

2. **Copy Files to Server:**
   ```bash
   scp -r dist/* user@server:/var/www/vessel-scheduler/
   scp -r modules/ requirements.txt *.py user@server:/opt/vessel-scheduler/
   ```

3. **Install Backend Dependencies:**
   ```bash
   ssh user@server
   cd /opt/vessel-scheduler
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure Service:**
   ```bash
   # Create systemd service
   sudo nano /etc/systemd/system/vessel-scheduler.service
   ```

   ```ini
   [Unit]
   Description=Vessel Scheduler API
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/opt/vessel-scheduler
   Environment="PATH=/opt/vessel-scheduler/venv/bin"
   ExecStart=/opt/vessel-scheduler/venv/bin/python api_server_enhanced.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

5. **Start Service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable vessel-scheduler
   sudo systemctl start vessel-scheduler
   ```

### Option 2: Docker Deployment

**Dockerfile:**

```dockerfile
# Multi-stage build
FROM node:18 AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM python:3.9-slim
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python app
COPY modules/ ./modules/
COPY *.py ./
COPY config.yaml ./

# Copy built frontend
COPY --from=frontend-builder /app/dist ./dist

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "api_server_enhanced.py"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./input:/app/input:ro
      - ./output:/app/output
      - ./logs:/app/logs
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./dist:/usr/share/nginx/html:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    restart: unless-stopped
```

**Deploy with Docker:**

```bash
docker-compose up -d --build
```

### Option 3: Cloud Platform Deployment

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init

# Create environment
eb create vessel-scheduler-prod

# Deploy
npm run build
eb deploy
```

#### Heroku

```bash
# Create Procfile
echo "web: python api_server_enhanced.py" > Procfile

# Deploy
heroku create vessel-scheduler
git push heroku main
```

#### DigitalOcean App Platform

- Connect GitHub repository
- Set build command: `npm run build`
- Set run command: `python api_server_enhanced.py`
- Configure environment variables in dashboard

---

## Server Configuration

### NGINX Configuration

**`/etc/nginx/sites-available/vessel-scheduler`:**

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Root directory
    root /var/www/vessel-scheduler;
    index index.html;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/json application/javascript;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff2|woff|ttf)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security - block access to sensitive files
    location ~ /\. {
        deny all;
    }
}
```

**Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/vessel-scheduler /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Performance Optimization

### Frontend Optimization

1. **Enable CDN for Static Assets**
   ```typescript
   // vite.config.ts
   export default defineConfig({
     build: {
       rollupOptions: {
         output: {
           assetFileNames: 'https://cdn.yourdomain.com/assets/[name]-[hash][extname]'
         }
       }
     }
   })
   ```

2. **Service Worker Caching**
   - Already configured in vite.config.ts
   - Assets cached for offline use
   - API responses cached with Network First strategy

3. **Image Optimization**
   ```bash
   # Install imagemin
   npm install --save-dev vite-plugin-imagemin

   # Use WebP format for smaller sizes
   ```

4. **Code Splitting**
   - Already implemented per route
   - Lazy load heavy components

### Backend Optimization

1. **Gunicorn for Production**
   ```bash
   pip install gunicorn

   # Run with multiple workers
   gunicorn -w 4 -b 0.0.0.0:5000 api_server_enhanced:app
   ```

2. **Caching with Redis**
   ```python
   from flask_caching import Cache
   
   cache = Cache(app, config={
       'CACHE_TYPE': 'redis',
       'CACHE_REDIS_URL': 'redis://localhost:6379/0'
   })
   
   @cache.cached(timeout=300)
   def expensive_calculation():
       # ...
   ```

3. **Database Connection Pooling**
   (If using PostgreSQL/MySQL)

---

## Security Hardening

### Application Security

1. **CORS Configuration**
   ```python
   from flask_cors import CORS
   
   CORS(app, origins=[
       'https://yourdomain.com',
       'https://www.yourdomain.com'
   ])
   ```

2. **Input Validation**
   ```python
   from flask import request
   from jsonschema import validate, ValidationError
   
   schema = {
       "type": "object",
       "properties": {
           "vessel_id": {"type": "string"},
           "quantity": {"type": "number", "minimum": 0}
       },
       "required": ["vessel_id", "quantity"]
   }
   
   try:
       validate(request.json, schema)
   except ValidationError as e:
       return jsonify({"error": str(e)}), 400
   ```

3. **Rate Limiting**
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(
       app,
       key_func=lambda: request.remote_addr,
       default_limits=["200 per day", "50 per hour"]
   )
   ```

### Server Security

1. **Firewall Configuration**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **Fail2Ban**
   ```bash
   sudo apt-get install fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

3. **Regular Updates**
   ```bash
   sudo apt-get update
   sudo apt-get upgrade
   ```

---

## Monitoring & Logging

### Application Monitoring

1. **Python Logging Configuration**
   ```python
   import logging
   from logging.handlers import RotatingFileHandler
   
   handler = RotatingFileHandler(
       'logs/app.log',
       maxBytes=10485760,  # 10MB
       backupCount=10
   )
   handler.setFormatter(logging.Formatter(
       '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
   ))
   app.logger.addHandler(handler)
   app.logger.setLevel(logging.INFO)
   ```

2. **Error Tracking (Sentry)**
   ```python
   import sentry_sdk
   from sentry_sdk.integrations.flask import FlaskIntegration
   
   sentry_sdk.init(
       dsn="your-sentry-dsn",
       integrations=[FlaskIntegration()],
       environment="production"
   )
   ```

3. **Performance Monitoring**
   ```python
   from flask import request
   import time
   
   @app.before_request
   def before_request():
       request.start_time = time.time()
   
   @app.after_request
   def after_request(response):
       if hasattr(request, 'start_time'):
           elapsed = time.time() - request.start_time
           app.logger.info(f'{request.method} {request.path} - {elapsed:.3f}s')
       return response
   ```

### Server Monitoring

**System Metrics:**
```bash
# Install monitoring tools
sudo apt-get install htop iotop nethogs

# Monitor logs
tail -f /var/log/nginx/access.log
tail -f /opt/vessel-scheduler/logs/app.log
```

**Uptime Monitoring:**
- Use services like UptimeRobot, Pingdom, or StatusCake
- Configure email/SMS alerts

---

## Backup & Recovery

### Automated Backups

**Backup Script (`backup.sh`):**

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/vessel-scheduler"
APP_DIR="/opt/vessel-scheduler"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz \
    $APP_DIR/input \
    $APP_DIR/output \
    $APP_DIR/logs \
    $APP_DIR/config.yaml

# Backup database (if applicable)
# pg_dump vessel_scheduler > $BACKUP_DIR/db_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Cron Job:**
```bash
# Run daily at 2 AM
0 2 * * * /opt/vessel-scheduler/backup.sh
```

### Recovery Procedure

```bash
# Restore from backup
cd /opt/vessel-scheduler
tar -xzf /backups/vessel-scheduler/app_20250126_020000.tar.gz

# Restart service
sudo systemctl restart vessel-scheduler
```

---

## Troubleshooting

### Common Issues

**Build Fails:**
```bash
# Clear caches
rm -rf node_modules dist .vite
npm install
npm run build
```

**Service Won't Start:**
```bash
# Check logs
sudo journalctl -u vessel-scheduler -n 50

# Check Python errors
cd /opt/vessel-scheduler
source venv/bin/activate
python api_server_enhanced.py
```

**High Memory Usage:**
```bash
# Check process
top -p $(pgrep -f api_server)

# Restart service
sudo systemctl restart vessel-scheduler
```

**NGINX 502 Bad Gateway:**
```bash
# Check if Flask is running
curl http://localhost:5000/api/health

# Check NGINX error log
sudo tail -f /var/log/nginx/error.log
```

### Health Checks

Add health check endpoint:

```python
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Code reviewed and approved
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Backups created

### Deployment

- [ ] Build artifacts created
- [ ] Files uploaded to server
- [ ] Dependencies installed
- [ ] Configuration files updated
- [ ] Database migrations run (if applicable)
- [ ] Services restarted
- [ ] NGINX configuration tested

### Post-Deployment

- [ ] Health check endpoint responding
- [ ] Frontend accessible
- [ ] API endpoints working
- [ ] Monitoring alerts configured
- [ ] Error tracking active
- [ ] Performance metrics baseline established
- [ ] Team notified of deployment

---

## Support & Maintenance

### Regular Maintenance Tasks

**Weekly:**
- Review error logs
- Check disk space
- Monitor performance metrics

**Monthly:**
- Update dependencies (security patches)
- Review and optimize database
- Test backup restoration

**Quarterly:**
- Security audit
- Performance optimization
- Capacity planning review

---

**Last Updated:** 2025-12-26  
**Version:** 2.0.0
