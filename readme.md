
# Deploy Django + Telegram Bot Project on Ubuntu Server

## 📦 Установка и настройка проекта

### 1. Обновите систему
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Установите зависимости
```bash
sudo apt install python3-pip python3.12-venv python3-dev libpq-dev postgresql postgresql-contrib nginx git -y
```

### 3. Клонируйте проект
```bash
git clone https://github.com/krisperiu/BotGazTB.git
cd BotGazTB
```

### 4. Настройка виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
sudo apt install nginx -y
```

### 5. Настройка базы данных PostgreSQL
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE yourdbname;
CREATE USER yourdbuser WITH PASSWORD 'yourpassword';
ALTER ROLE yourdbuser SET client_encoding TO 'utf8';
ALTER ROLE yourdbuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE yourdbuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE yourdbname TO yourdbuser;
\q
```

### 6. Настройка Django
Создайте `.env` файл :
```env
TOKEN=7137085581:AAFWlcpjSZcC16At8k6f9x-wbnSFYALQ598
SQLALCHEMY_URL=postgresql+asyncpg://USER:PASS@localhost/DBNAME
DJANGO_SECRET_KEY = django-insecure-ykat_-7_t+$@uu@zg%$-jt_*o09yv0i15u(j0z-&y$dj(8m)!$
DB_PASSWORD = 
```

Примените миграции и соберите статику:
```bash
python manage.py migrate
python manage.py collectstatic
```

### 7. Настройка Gunicorn
Создайте сервисный файл:
```bash
sudo nano /etc/systemd/system/botreports.service
```

```ini
[Unit]
Description=Gunicorn instance to serve Django botreports project
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/home/BotGazTB/botreports

ExecStart=/home/BotGazTB/venv/bin/gunicorn \
          --access-logfile - \
          --workers 1 \
          --threads 1 \
          --timeout 30 \
          --bind unix:/home/BotGazTB/botreports/botreports.sock \
          botreports.wsgi:application

Restart=on-failure
RestartSec=5

MemoryMax=130M
CPUQuota=40%

StartLimitIntervalSec=60
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
```

### 8. Настройка Telegram-бота
Создайте `telegram-bot.service`:
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

```ini
[Unit]
Description=Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
User=root
WorkingDirectory=/home/youruser/project
ExecStart=/home/youruser/project/venv/bin/python /home/youruser/project/run.py

Restart=on-failure
RestartSec=10s

MemoryMax=180M
CPUQuota=40%

[Install]
WantedBy=multi-user.target
```

Запустите сервисы:
```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable django telegram-bot
sudo systemctl start django telegram-bot
```

### 9. Настройка Nginx
```bash
sudo nano /etc/nginx/sites-available/botreports   
```

```nginx
server {
    listen 80;
    server_name 195.133.31.208;

    location / {
        proxy_pass http://unix:/home/BotGazTB/botreports/botreports.sock;
        include proxy_params;
        proxy_redirect off;
    }

    location /static/ {
        alias /home/BotGazTB/botreports/staticfiles/;
    }

    location /media/ {
        alias /home/BotGazTB/botreports/media/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/botreports /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

---

##  Готово!