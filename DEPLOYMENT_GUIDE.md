# Deployment Guide - EC2 Deployment

## Overview
This guide walks you through deploying your Electronic Inventory System to AWS EC2.

## Prerequisites

Before starting, make sure you have completed:
- ✅ AWS account created
- ✅ S3 bucket created
- ✅ RDS PostgreSQL database created
- ✅ SES email verified
- ✅ IAM user with access keys created
- ✅ EC2 instance launched
- ✅ SSH key (.pem file) downloaded

---

## Part 1: Connect to EC2 Instance

### For Windows Users:

1. **Install PuTTY** (if not already installed):
   - Download from: https://www.putty.org/
   - Install PuTTY and PuTTYgen

2. **Convert .pem to .ppk** (if you downloaded .pem):
   - Open PuTTYgen
   - Click "Load" and select your `.pem` file
   - Click "Save private key"
   - Save as `inventory-key.ppk`

3. **Connect using PuTTY**:
   - Open PuTTY
   - **Host Name**: `ubuntu@YOUR-EC2-PUBLIC-IP`
   - **Port**: 22
   - Go to Connection → SSH → Auth
   - Browse and select your `.ppk` file
   - Click "Open"
   - Click "Yes" if you see security alert

### For Mac/Linux Users:

```bash
# Make key file readable only by you
chmod 400 inventory-key.pem

# Connect to EC2
ssh -i inventory-key.pem ubuntu@YOUR-EC2-PUBLIC-IP
```

---

## Part 2: Prepare Project Files

### Option A: Upload via SCP (Recommended)

**On your local machine** (Windows PowerShell or Mac/Linux Terminal):

```bash
# Navigate to your project directory
cd c:\Learn\PythonProject\electronic_inventory

# Create a zip file (Windows PowerShell)
Compress-Archive -Path * -DestinationPath inventory.zip

# Or on Mac/Linux
# zip -r inventory.zip .

# Upload to EC2 (replace YOUR-EC2-IP and path to key)
scp -i inventory-key.pem inventory.zip ubuntu@YOUR-EC2-IP:~/
```

### Option B: Use Git (Alternative)

**On EC2 instance**:
```bash
cd ~
git clone YOUR-GITHUB-REPO-URL inventory
```

---

## Part 3: Setup EC2 Instance

**Run these commands on your EC2 instance** (after SSH connection):

### 1. Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Install Python 3.11
```bash
sudo apt-get install -y python3.11 python3.11-venv python3-pip
sudo apt-get install -y python3.11-dev libpq-dev build-essential
```

### 3. Install PostgreSQL Client
```bash
sudo apt-get install -y postgresql-client
```

### 4. Install Nginx
```bash
sudo apt-get install -y nginx
```

### 5. Create Application Directory
```bash
sudo mkdir -p /var/www/inventory
sudo chown -R ubuntu:ubuntu /var/www/inventory
```

### 6. Extract Project Files
```bash
# If you uploaded zip file
sudo apt-get install -y unzip
unzip ~/inventory.zip -d /var/www/inventory/

# Or if using git
# mv ~/inventory/* /var/www/inventory/
```

### 7. Navigate to Project
```bash
cd /var/www/inventory
```

### 8. Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 9. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn boto3 watchtower
```

---

## Part 4: Configure Environment

### 1. Create .env File

```bash
cd /var/www/inventory
nano .env
```

**Paste this content** (replace with your actual values):

```bash
# Django Settings
SECRET_KEY=your-generated-secret-key-here-make-it-long-and-random
DEBUG=False
ALLOWED_HOSTS=your-ec2-public-ip,your-ec2-dns,localhost

# AWS RDS PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=inventorydb
DB_USER=postgres
DB_PASSWORD=YOUR-RDS-PASSWORD
DB_HOST=YOUR-RDS-ENDPOINT.rds.amazonaws.com
DB_PORT=5432

# AWS Credentials
AWS_ACCESS_KEY_ID=YOUR-ACCESS-KEY-ID
AWS_SECRET_ACCESS_KEY=YOUR-SECRET-ACCESS-KEY
AWS_REGION=us-east-1

# AWS S3 Storage
AWS_STORAGE_BUCKET_NAME=electronic-inventory-storage
AWS_S3_CUSTOM_DOMAIN=electronic-inventory-storage.s3.amazonaws.com

# AWS SES Email
AWS_SES_REGION=us-east-1
SES_FROM_EMAIL=your-verified-email@example.com

# Application Settings
LOW_STOCK_ALERT_EMAIL=your-email@example.com
ADMIN_EMAIL=your-email@example.com
```

**Save**: Press `Ctrl+X`, then `Y`, then `Enter`

### 2. Generate Secret Key

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and update `SECRET_KEY` in `.env`

---

## Part 5: Database Setup

### 1. Test RDS Connection
```bash
psql -h YOUR-RDS-ENDPOINT.rds.amazonaws.com -U postgres -d inventorydb
# Enter your password when prompted
# Type \q to exit
```

### 2. Run Migrations
```bash
cd /var/www/inventory/inventory_project
source ../venv/bin/activate
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 5. Load Sample Data (Optional)
```bash
python create_sample_data.py
```

---

## Part 6: Configure Gunicorn

### 1. Test Gunicorn
```bash
cd /var/www/inventory/inventory_project
gunicorn --bind 0.0.0.0:8000 inventory_project.wsgi:application
```

Press `Ctrl+C` to stop after verifying it works.

### 2. Create Gunicorn Service

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

**Paste this**:

```ini
[Unit]
Description=Gunicorn daemon for Django Inventory App
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/inventory/inventory_project
Environment="PATH=/var/www/inventory/venv/bin"
ExecStart=/var/www/inventory/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/inventory/inventory.sock \
          inventory_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Save**: `Ctrl+X`, `Y`, `Enter`

### 3. Start Gunicorn
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

---

## Part 7: Configure Nginx

### 1. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/inventory
```

**Paste this**:

```nginx
server {
    listen 80;
    server_name YOUR-EC2-PUBLIC-IP YOUR-EC2-DNS;

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    location /static/ {
        alias /var/www/inventory/inventory_project/staticfiles/;
    }

    location /media/ {
        alias /var/www/inventory/inventory_project/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/inventory/inventory.sock;
    }
}
```

**Save**: `Ctrl+X`, `Y`, `Enter`

### 2. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/inventory /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## Part 8: Configure Security Group

Go back to **AWS Console** → **EC2** → **Security Groups**:

1. Find `inventory-server-sg`
2. Click **"Inbound rules"** → **"Edit inbound rules"**
3. Ensure these ports are open:
   - **SSH (22)**: Your IP
   - **HTTP (80)**: 0.0.0.0/0 (Anywhere)
   - **HTTPS (443)**: 0.0.0.0/0 (Anywhere)
4. Click **"Save rules"**

---

## Part 9: Test Deployment

### 1. Access Website
Open browser and go to:
```
http://YOUR-EC2-PUBLIC-IP/
```

You should see the login page!

### 2. Login
Use the superuser credentials you created earlier.

### 3. Test Features
- View dashboard
- Add products
- Upload images (will go to S3)
- Create transactions

---

## Part 10: Setup CloudWatch Monitoring

CloudWatch is already integrated! Logs are sent automatically when:
- Low stock alerts are triggered
- Errors occur
- Important events happen

**View logs**:
1. Go to AWS Console → CloudWatch
2. Click "Log groups"
3. Find `/aws/inventory-app`
4. View application logs

---

## Part 11: Setup Low Stock Email Alerts

### Manual Check
```bash
cd /var/www/inventory/inventory_project
source ../venv/bin/activate
python manage.py check_low_stock
```

### Automated Daily Checks (Cron Job)
```bash
crontab -e
```

**Add this line** (runs daily at 9 AM):
```bash
0 9 * * * /var/www/inventory/venv/bin/python /var/www/inventory/inventory_project/manage.py check_low_stock
```

Save and exit.

---

## Troubleshooting

### Application won't start
```bash
# Check Gunicorn logs
sudo journalctl -u gunicorn -e

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Can't connect to database
```bash
# Test RDS connection
psql -h YOUR-RDS-ENDPOINT -U postgres -d inventorydb

# Check .env file
cat /var/www/inventory/.env

# Verify RDS security group allows EC2 access
```

### Static files not loading
```bash
# Recollect static files
python manage.py collectstatic --noinput

# Check Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Images not uploading to S3
```bash
# Check AWS credentials in .env
# Verify S3 bucket permissions
# Check CloudWatch logs for errors
```

---

## Useful Commands

```bash
# Restart application
sudo systemctl restart gunicorn

# View application logs
sudo journalctl -u gunicorn -f

# Check service status
sudo systemctl status gunicorn
sudo systemctl status nginx

# Django management
cd /var/www/inventory/inventory_project
source ../venv/bin/activate
python manage.py <command>

# Update code
cd /var/www/inventory
git pull  # if using git
sudo systemctl restart gunicorn
```

---

## Success Checklist

- [ ] EC2 instance accessible via SSH
- [ ] Python 3.11 installed
- [ ] All dependencies installed
- [ ] .env file configured with AWS credentials
- [ ] Database migrations successful
- [ ] Superuser created
- [ ] Static files collected
- [ ] Gunicorn service running
- [ ] Nginx service running
- [ ] Website accessible at http://EC2-IP/
- [ ] Can login to admin panel
- [ ] Images upload to S3
- [ ] Low stock emails send via SES
- [ ] CloudWatch receiving logs

---

## Next Steps

1. **Domain Name** (Optional): Configure Route 53 for custom domain
2. **HTTPS**: Set up SSL certificate with Let's Encrypt
3. **Backups**: Configure automated RDS backups
4. **Monitoring**: Set up CloudWatch alarms
5. **Scaling**: Add load balancer if needed

**Congratulations! Your application is now deployed on AWS!** 🎉
