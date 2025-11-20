# AWS Services Integration Documentation

## Overview
This document explains how the 5 AWS services are integrated into the Electronic Inventory Management System.

---

## Service #1: Amazon EC2 (Elastic Compute Cloud)

### Purpose
Host and run the Django web application.

### What It Does
- Runs the web server (Nginx + Gunicorn)
- Executes Django application code
- Serves HTTP requests from users
- Processes business logic

### Technical Details
- **Instance Type**: t2.micro (1 vCPU, 1 GB RAM)
- **OS**: Ubuntu Server 22.04 LTS
- **Web Server**: Nginx (reverse proxy)
- **App Server**: Gunicorn (WSGI server)
- **Python**: 3.11.9

### Files Involved
- `deploy_to_ec2.sh` - Deployment script
- `DEPLOYMENT_GUIDE.md` - Step-by-step deployment

### How to Use
```bash
# SSH into EC2
ssh -i inventory-key.pem ubuntu@YOUR-EC2-IP

# Manage application
sudo systemctl restart gunicorn
sudo systemctl status nginx
```

---

## Service #2: Amazon RDS (Relational Database Service)

### Purpose
Managed PostgreSQL database for storing all inventory data.

### What It Does
- Stores products, categories, transactions
- Manages user accounts and authentication
- Provides data persistence
- Handles database backups automatically

### Technical Details
- **Engine**: PostgreSQL 15.x
- **Instance Class**: db.t3.micro
- **Storage**: 20 GB SSD
- **Multi-AZ**: Disabled (to save costs)
- **Backups**: Can be enabled for production

### Data Stored
1. **Products**: Name, SKU, quantity, prices, images
2. **Categories**: Electronics categories
3. **Transactions**: Stock in/out movements
4. **Users**: Admin and staff accounts
5. **Django Tables**: Sessions, permissions, etc.

### Files Involved
- `settings.py` - Database configuration
- `.env` - Database credentials

### Configuration in Code
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventorydb',
        'USER': 'postgres',
        'PASSWORD': 'from .env',
        'HOST': 'your-rds-endpoint.rds.amazonaws.com',
        'PORT': '5432',
    }
}
```

### How to Use
```bash
# Connect to database
psql -h YOUR-RDS-ENDPOINT -U postgres -d inventorydb

# Run migrations
python manage.py migrate

# Backup database
pg_dump -h YOUR-RDS-ENDPOINT -U postgres inventorydb > backup.sql
```

---

## Service #3: Amazon S3 (Simple Storage Service)

### Purpose
Store product images, datasheets, and static files (CSS, JS).

### What It Does
- Stores product images uploaded by users
- Stores PDF datasheets for components
- Hosts static files (CSS, JavaScript, fonts)
- Provides public URLs for images
- Handles file versioning and storage

### Technical Details
- **Bucket Name**: electronic-inventory-storage
- **Region**: us-east-1
- **Access**: Public read for images
- **Storage Class**: Standard
- **Versioning**: Optional

### Files Involved
- `settings.py` - S3 configuration
- `aws_utils.py` - S3 helper functions
- `models.py` - ImageField/FileField definitions

### Configuration in Code
```python
# settings.py
AWS_STORAGE_BUCKET_NAME = 'electronic-inventory-storage'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Automatic S3 upload when saving images
product.image = uploaded_file
product.save()  # Automatically uploads to S3
```

### Folder Structure in S3
```
electronic-inventory-storage/
├── products/
│   ├── arduino-uno.jpg
│   ├── esp32.jpg
│   └── raspberry-pi.jpg
├── datasheets/
│   ├── arduino-uno-datasheet.pdf
│   └── esp32-datasheet.pdf
└── static/
    ├── css/
    ├── js/
    └── admin/
```

### How to Use
```bash
# Via Django Admin
# Just upload files normally - they go to S3 automatically

# Via AWS CLI
aws s3 ls s3://electronic-inventory-storage/
aws s3 cp file.jpg s3://electronic-inventory-storage/products/

# Via Python
from inventory.aws_utils import S3StorageHelper
url = S3StorageHelper.upload_file(file_obj, 'products/new-image.jpg')
```

---

## Service #4: Amazon SES (Simple Email Service)

### Purpose
Send email notifications for low stock alerts and system notifications.

### What It Does
- Sends low stock alert emails to administrators
- Sends password reset emails
- Sends system notifications
- Provides reliable email delivery
- Tracks email metrics

### Technical Details
- **SMTP Endpoint**: email-smtp.us-east-1.amazonaws.com
- **Port**: 587 (TLS)
- **Authentication**: SMTP credentials
- **Sending Limit**: 62,000 emails/month (free tier)
- **Sandbox Mode**: Only verified emails (request production access for any email)

### Files Involved
- `aws_utils.py` - Email alert service
- `management/commands/check_low_stock.py` - Alert command
- `settings.py` - Email configuration

### Configuration in Code
```python
# settings.py
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION = 'us-east-1'
SES_FROM_EMAIL = 'your-verified-email@example.com'

# Send email
from django.core.mail import send_mail

send_mail(
    subject='Low Stock Alert',
    message='ESP32 is running low (8 units left)',
    from_email=settings.SES_FROM_EMAIL,
    recipient_list=['admin@example.com'],
)
```

### Email Triggers
1. **Low Stock Alerts**: Automatic daily check
2. **Password Reset**: When user requests password reset
3. **New User**: Welcome email (can be configured)
4. **Critical Alerts**: When stock reaches zero

### How to Use
```bash
# Manual alert check
python manage.py check_low_stock

# Setup automated daily alerts (cron)
0 9 * * * /path/to/venv/bin/python /path/to/manage.py check_low_stock

# Send test email via Django shell
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'This is a test', 'from@example.com', ['to@example.com'])
```

### Sample Alert Email
```
Subject: Low Stock Alert - 2 Items Need Restocking

Low Stock Alert - Electronic Inventory System
==================================================

The following 2 items are running low on stock:

- ESP32 DevKit (SKU: MCU-ESP-32): 8 units (Min: 10)
- 9V Battery (SKU: PWR-BAT-9V): 6 units (Min: 12)

==================================================
Please restock these items soon.

Login to manage inventory: http://your-server-url/admin/
```

---

## Service #5: Amazon CloudWatch

### Purpose
Monitor application logs, metrics, and performance.

### What It Does
- Collects application logs
- Monitors error rates
- Tracks low stock alert events
- Stores system metrics
- Provides debugging information
- Enables performance monitoring

### Technical Details
- **Log Group**: `/aws/inventory-app`
- **Log Stream**: `application-logs`
- **Retention**: Configurable (default: indefinite)
- **Metrics**: Custom application metrics
- **Alarms**: Can be configured

### Files Involved
- `aws_utils.py` - CloudWatch logging class
- `views.py` - Event logging
- `management/commands/` - Command logging

### Configuration in Code
```python
# aws_utils.py
from inventory.aws_utils import AWSCloudWatch, log_to_cloudwatch

# Initialize CloudWatch
cloudwatch = AWSCloudWatch()

# Log events
cloudwatch.log_event('Low stock alert sent for 2 items', level='WARNING')
log_to_cloudwatch('User logged in successfully', level='INFO')
log_to_cloudwatch('Database connection failed', level='ERROR')
```

### Logged Events
1. **Application Startup**: Server started
2. **Low Stock Alerts**: Alert triggered for X items
3. **Errors**: Database errors, S3 upload failures
4. **User Actions**: Login, logout, product updates
5. **System Events**: Scheduled tasks, background jobs

### Log Levels
- **INFO**: Normal operations
- **WARNING**: Low stock alerts, recoverable errors
- **ERROR**: Failed operations, exceptions
- **CRITICAL**: System failures

### How to Use
```bash
# View logs in AWS Console
# 1. Go to CloudWatch
# 2. Click "Log groups"
# 3. Select "/aws/inventory-app"
# 4. View recent logs

# Query logs via AWS CLI
aws logs tail /aws/inventory-app --follow

# Search for errors
aws logs filter-log-events \
    --log-group-name /aws/inventory-app \
    --filter-pattern "ERROR"
```

### Sample CloudWatch Logs
```
2025-11-17 09:00:01 [INFO] Application started successfully
2025-11-17 09:15:23 [INFO] User admin logged in
2025-11-17 09:15:45 [INFO] Product ESP32 updated - quantity changed from 10 to 8
2025-11-17 09:00:00 [WARNING] Low stock alert sent for 2 items
2025-11-17 10:30:12 [ERROR] Failed to upload image to S3: Access Denied
2025-11-17 11:00:00 [INFO] Low stock check command executed successfully
```

### Setting Up Alarms (Optional)
1. Go to CloudWatch → Alarms
2. Create alarm for error count
3. Set threshold (e.g., > 10 errors in 5 minutes)
4. Configure SNS notification
5. Receive alerts via email/SMS

---

## Integration Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Request                             │
│                              ↓                                   │
│                    ┌──────────────────┐                         │
│                    │   EC2 Instance   │                         │
│                    │   (Web Server)   │                         │
│                    └────────┬─────────┘                         │
│                             │                                    │
│            ┌────────────────┼────────────────┐                  │
│            ↓                ↓                ↓                   │
│     ┌──────────┐     ┌──────────┐    ┌──────────┐             │
│     │   RDS    │     │    S3    │    │CloudWatch│             │
│     │(Database)│     │(Storage) │    │  (Logs)  │             │
│     └──────────┘     └──────────┘    └──────────┘             │
│                             │                                    │
│                             ↓                                    │
│                      ┌──────────┐                               │
│                      │   SES    │                               │
│                      │ (Email)  │                               │
│                      └──────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cost Breakdown (AWS Free Tier)

### Month 1-12 (Free Tier):

| Service | Free Tier | Estimated Cost |
|---------|-----------|----------------|
| EC2 t2.micro | 750 hours/month | $0 |
| RDS db.t3.micro | 750 hours/month | $0 |
| S3 Storage | 5 GB + 20K requests | $0 |
| SES | 62,000 emails | $0 |
| CloudWatch | 10 metrics + 5GB logs | $0 |
| **Total** | | **$0 - $5/month** |

### After Free Tier (Month 13+):

| Service | Cost |
|---------|------|
| EC2 t2.micro | ~$8-10/month |
| RDS db.t3.micro | ~$12-15/month |
| S3 Storage (10GB) | ~$0.23/month |
| SES (10,000 emails) | ~$1/month |
| CloudWatch | ~$3/month |
| **Total** | **~$25-30/month** |

---

## Best Practices

### Security
- ✅ Use environment variables for credentials
- ✅ Enable S3 bucket versioning
- ✅ Configure RDS security groups properly
- ✅ Use IAM roles with minimal permissions
- ✅ Enable CloudWatch for monitoring
- ✅ Regular database backups
- ✅ Keep software updated

### Performance
- ✅ Use S3 for static files (offload from EC2)
- ✅ Configure Nginx caching
- ✅ Optimize database queries
- ✅ Monitor CloudWatch metrics
- ✅ Set up connection pooling

### Cost Optimization
- ✅ Use free tier resources
- ✅ Stop EC2 instances when not in use
- ✅ Set S3 lifecycle policies
- ✅ Configure CloudWatch log retention
- ✅ Delete unused snapshots
- ✅ Monitor AWS Cost Explorer

---

## Troubleshooting Common Issues

### S3 Upload Fails
```python
# Check: AWS credentials in .env
# Check: S3 bucket permissions
# Check: Bucket policy allows uploads
# View CloudWatch logs for details
```

### Email Not Sending
```python
# Check: Email verified in SES
# Check: SES still in sandbox mode?
# Check: SMTP credentials correct
# Check: CloudWatch logs for SES errors
```

### Database Connection Error
```python
# Check: RDS security group allows EC2 IP
# Check: RDS endpoint correct in .env
# Check: Database credentials correct
# Test: psql -h RDS-ENDPOINT -U postgres -d inventorydb
```

### CloudWatch Logs Not Appearing
```python
# Check: AWS credentials valid
# Check: IAM user has CloudWatch permissions
# Check: Log group created
# Manual test: python manage.py check_low_stock
```

---

## Testing AWS Integration

### 1. Test S3 Upload
```bash
# Upload product image via admin panel
# Verify image appears in S3 bucket
# Check image URL works
```

### 2. Test SES Email
```bash
# Run: python manage.py check_low_stock
# Check email inbox
# Verify email received
```

### 3. Test RDS Database
```bash
# Create product via admin
# Verify data saved in RDS
# Check: psql -h RDS-ENDPOINT -U postgres -d inventorydb
```

### 4. Test CloudWatch Logging
```bash
# Trigger any action
# Go to CloudWatch console
# Check logs appear
```

### 5. Test Full Workflow
1. Login to admin
2. Add new product with image → **Tests S3**
3. Set low quantity → **Tests RDS**
4. Run check_low_stock → **Tests SES + CloudWatch**
5. Check CloudWatch logs → **Tests CloudWatch**

---

## Summary

### ✅ All 5 AWS Services Integrated:

1. **EC2** - Hosts the application
2. **RDS** - Stores all data
3. **S3** - Stores images and files
4. **SES** - Sends email alerts
5. **CloudWatch** - Monitors everything

### Ready for Production:
- Scalable architecture
- Managed services
- Automatic backups available
- Monitoring and logging
- Cost-effective
- Production-ready

**Your inventory system is now a full-fledged cloud application!** 🚀
