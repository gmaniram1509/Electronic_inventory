# Setup Guide - 5 Additional AWS Services

## Prerequisites
✅ Complete `AWS_SETUP_GUIDE.md` first (EC2, RDS, S3, SES, CloudWatch)
✅ AWS account with admin access
✅ AWS CLI installed (optional)

---

## Service #6: AWS SNS (Simple Notification Service)

### Purpose
Real-time push notifications for inventory alerts

### Step-by-Step Setup

1. **Go to AWS Console** → Search "SNS"

2. **Create Topic:**
   - Click **"Create topic"**
   - **Type:** Standard
   - **Name:** `inventory-alerts`
   - **Display name:** `Inventory Notifications`
   - Click **"Create topic"**

3. **Note the Topic ARN:**
   - Copy the ARN (looks like: `arn:aws:sns:us-east-1:123456789:inventory-alerts`)
   - Save for `.env` file

4. **Create Subscription:**
   - Click **"Create subscription"**
   - **Protocol:** Email
   - **Endpoint:** Your email address
   - Click **"Create subscription"**
   - **Check your email** and confirm subscription

5. **Add to `.env`:**
   ```
   SNS_TOPIC_ARN=arn:aws:sns:us-east-1:YOUR_ACCOUNT:inventory-alerts
   ```

**Test:**
```bash
python manage.py shell
>>> from inventory.aws_utils import send_sns_notification
>>> send_sns_notification('Test', 'Hello from Django!')
# Check your email!
```

---

## Service #7: AWS DynamoDB

### Purpose
Activity and audit logging (separate from main database)

### Step-by-Step Setup

1. **Go to AWS Console** → Search "DynamoDB"

2. **Create Table:**
   - Click **"Create table"**
   - **Table name:** `inventory-logs`
   - **Partition key:** `log_id` (String)
   - **Sort key:** `timestamp` (Number)
   - **Table settings:** Default settings
   - **Read/write capacity:** On-demand
   - Click **"Create table"**

3. **Wait** for table creation (~1 minute)

4. **Add to `.env`:**
   ```
   DYNAMODB_TABLE_NAME=inventory-logs
   ```

**Auto-Created:**
The application will automatically create the table if it doesn't exist!

**Test:**
```bash
python manage.py shell
>>> from inventory.aws_utils import log_activity_to_dynamodb
>>> log_activity_to_dynamodb('TEST', 'Product', '1', 'Test log entry')
# Check DynamoDB console - should see entry!
```

---

## Service #8: AWS Lambda

### Purpose
Serverless transaction processing

### Step-by-Step Setup

1. **Go to AWS Console** → Search "Lambda"

2. **Create Function:**
   - Click **"Create function"**
   - **Option:** Author from scratch
   - **Function name:** `inventory-transaction-processor`
   - **Runtime:** Python 3.11
   - **Architecture:** x86_64
   - **Permissions:** Create new role with basic Lambda permissions
   - Click **"Create function"**

3. **Upload Code:**
   - Scroll to **"Code source"**
   - Delete existing code
   - Copy contents of `lambda_function.py` from project
   - Paste into editor
   - Click **"Deploy"**

4. **Configure:**
   - **Timeout:** 30 seconds
   - **Memory:** 128 MB

5. **Set Environment Variables:**
   - Click **"Configuration"** → **"Environment variables"**
   - Add:
     - `DYNAMODB_TABLE`: `inventory-transaction-logs`

6. **Add Permissions:**
   - Go to **"Configuration"** → **"Permissions"**
   - Click role name
   - Add policy: `AmazonDynamoDBFullAccess`

7. **Add to `.env`:**
   ```
   LAMBDA_FUNCTION_NAME=inventory-transaction-processor
   ```

**Test:**
```bash
python manage.py shell
>>> from inventory.models import Transaction, Product
>>> p = Product.objects.first()
>>> t = Transaction.objects.create(product=p, transaction_type='IN', quantity=10)
# Lambda should be triggered automatically!
# Check Lambda logs in CloudWatch
```

---

## Service #9: AWS ElastiCache (Redis)

### Purpose
In-memory caching for better performance

### Step-by-Step Setup

1. **Go to AWS Console** → Search "ElastiCache"

2. **Create Redis Cluster:**
   - Click **"Create"** → **"Redis cache"**
   - **Cluster mode:** Disabled
   - **Name:** `inventory-cache`
   - **Engine version:** 7.x
   - **Node type:** `cache.t2.micro` (Free tier)
   - **Number of replicas:** 0
   - **Subnet group:** Create new (use default VPC)
   - **Security group:** Create new or use existing
     - **Important:** Allow inbound port 6379 from EC2 security group

3. **Wait** for creation (~5-10 minutes)

4. **Get Endpoint:**
   - Click on cluster name
   - Copy **Primary Endpoint** (looks like: `xxx.cache.amazonaws.com:6379`)

5. **Update Security Group:**
   - Go to EC2 → Security Groups
   - Find ElastiCache security group
   - Add inbound rule:
     - **Type:** Custom TCP
     - **Port:** 6379
     - **Source:** EC2 security group

6. **Add to `.env`:**
   ```
   ELASTICACHE_ENDPOINT=your-cluster.cache.amazonaws.com
   REDIS_URL=redis://your-cluster.cache.amazonaws.com:6379/0
   ```

7. **Update `settings.py`:**
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/0'),
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
           }
       }
   }
   ```

**Test:**
```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'Hello Redis!', 60)
>>> print(cache.get('test'))
# Should print: Hello Redis!
```

---

## Service #10: AWS Secrets Manager

### Purpose
Secure storage for passwords and API keys

### Step-by-Step Setup

1. **Go to AWS Console** → Search "Secrets Manager"

2. **Create Secret for Database:**
   - Click **"Store a new secret"**
   - **Secret type:** Other type of secret
   - **Key/value pairs:**
     - Key: `username`, Value: `postgres`
     - Key: `password`, Value: `YOUR_RDS_PASSWORD`
     - Key: `host`, Value: `YOUR_RDS_ENDPOINT`
     - Key: `port`, Value: `5432`
     - Key: `database`, Value: `inventorydb`
   - Click **"Next"**
   - **Secret name:** `inventory/database`
   - Click **"Next"** → **"Next"** → **"Store"**

3. **Create Secret for Application:**
   - Repeat above with:
   - **Secret name:** `inventory/application`
   - **Key/value pairs:**
     - Key: `secret_key`, Value: `YOUR_DJANGO_SECRET_KEY`
     - Key: `aws_access_key`, Value: `YOUR_AWS_KEY`
     - Key: `aws_secret_key`, Value: `YOUR_AWS_SECRET`

4. **Add to `.env`:**
   ```
   SECRETS_MANAGER_ENABLED=True
   DB_SECRET_NAME=inventory/database
   APP_SECRET_NAME=inventory/application
   ```

5. **Update IAM Permissions:**
   - IAM user needs `SecretsManagerReadWrite` policy

**Test:**
```bash
python manage.py shell
>>> from inventory.aws_utils import AWSSecretsManager
>>> sm = AWSSecretsManager()
>>> secret = sm.get_secret('inventory/database')
>>> print(secret)
# Should print database credentials
```

---

## 📝 Complete `.env` File

After setting up all services, your `.env` should look like:

```bash
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-ec2-ip,your-domain.com

# RDS Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=inventorydb
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=5432

# AWS Credentials
AWS_ACCESS_KEY_ID=YOUR_KEY_ID
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
AWS_REGION=us-east-1

# S3
AWS_STORAGE_BUCKET_NAME=electronic-inventory-storage
AWS_S3_CUSTOM_DOMAIN=electronic-inventory-storage.s3.amazonaws.com

# SES
AWS_SES_REGION=us-east-1
SES_FROM_EMAIL=verified@email.com

# SNS
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT:inventory-alerts

# DynamoDB
DYNAMODB_TABLE_NAME=inventory-logs

# Lambda
LAMBDA_FUNCTION_NAME=inventory-transaction-processor

# ElastiCache
REDIS_URL=redis://your-cache.cache.amazonaws.com:6379/0

# Secrets Manager
SECRETS_MANAGER_ENABLED=True
DB_SECRET_NAME=inventory/database
```

---

## ✅ Verification Checklist

Test each service:

- [ ] **SNS:** Send test notification, receive email
- [ ] **DynamoDB:** Create product, check logs table
- [ ] **Lambda:** Create transaction, check Lambda logs
- [ ] **ElastiCache:** Cache data, retrieve from cache
- [ ] **Secrets Manager:** Retrieve secret successfully

---

## 🎉 Done!

You now have **10 AWS services** integrated:

1. ✅ EC2 - Hosting
2. ✅ RDS - Database
3. ✅ S3 - File storage (with auto-delete!)
4. ✅ SES - Email
5. ✅ CloudWatch - Monitoring
6. ✅ SNS - Notifications
7. ✅ DynamoDB - Activity logs
8. ✅ Lambda - Async processing
9. ✅ ElastiCache - Caching
10. ✅ Secrets Manager - Secure credentials

**Your system is now enterprise-ready!** 🚀

---

## 💡 Tips

- **Start Simple:** Set up one service at a time
- **Test Each:** Verify working before moving to next
- **Save ARNs:** Keep all ARNs and endpoints in notes
- **Check Logs:** Use CloudWatch to debug issues
- **Monitor Costs:** Check AWS billing dashboard regularly

---

## 🆘 Troubleshooting

### SNS not sending:
- Check email subscription confirmed
- Verify Topic ARN correct
- Check IAM permissions

### DynamoDB errors:
- Table must exist (auto-created by app)
- Check table name matches
- Verify IAM permissions

### Lambda not triggered:
- Check function name matches
- Verify IAM permissions
- Check CloudWatch logs

### ElastiCache connection fails:
- Security group must allow port 6379
- Endpoint must be correct
- Redis must be running

### Secrets Manager access denied:
- IAM user needs read permissions
- Secret name must match exactly
- Check AWS region

---

**Need Help?** Check `AWS_10_SERVICES_GUIDE.md` for complete documentation!
