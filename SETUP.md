# Detailed Setup Guide

## Prerequisites
- Python 3.8+
- AWS Account with appropriate credentials
- PostgreSQL (optional, SQLite works for development)

## Step-by-Step Setup

### 1. Extract and Setup Virtual Environment
```bash
unzip electronic_inventory.zip
cd electronic_inventory
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure AWS Services

#### S3 Bucket
```bash
aws s3 mb s3://electronic-inventory-bucket
```

#### DynamoDB Table
```bash
aws dynamodb create-table \
    --table-name inventory-logs \
    --attribute-definitions AttributeName=log_id,AttributeType=S \
    --key-schema AttributeName=log_id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

#### SNS Topic
```bash
aws sns create-topic --name inventory-alerts
```

#### SES Email Verification
```bash
aws ses verify-email-identity --email-address your-email@domain.com
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
nano .env  # Update with your credentials
```

### 5. Run Migrations
```bash
cd inventory_project
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Admin User
```bash
python manage.py createsuperuser
```

### 7. Create Sample Categories
```bash
python manage.py shell
>>> from inventory.models import Category
>>> Category.objects.create(name="Microcontrollers")
>>> Category.objects.create(name="Sensors")
>>> Category.objects.create(name="Power Supplies")
>>> exit()
```

### 8. Run the Server
```bash
python manage.py runserver
```

Visit http://localhost:8000
