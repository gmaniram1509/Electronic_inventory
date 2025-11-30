# Electronic Inventory Management System

A Django-based electronic inventory management system integrated with **10 AWS services** for enterprise-grade cloud deployment.

##  Quick Start (For First-Time Users)

### Prerequisites
- Python 3.11 installed (Download from: https://www.python.org/downloads/)
- Command Prompt / Terminal

### Setup in 5 Minutes

```bash
# 1. Navigate to project directory
cd electronic_inventory

# 2. Create virtual environment
py -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Setup database
cd inventory_project
python manage.py migrate

# 6. Start server
python manage.py runserver
```

### Login Credentials

**URL:** http://localhost:8000/

**Username:** `admin`
**Password:** `admin123`

**Admin Panel:** http://localhost:8000/admin/


---

## ✨ Features

- 📦 Product management with image uploads
- 📊 Real-time inventory tracking
- 🔄 Stock in/out transactions
- ⚠️ Low stock alerts and email notifications
- 📁 Category-based organization
- 🔍 Search and filtering
- 👥 User management and permissions
- 📈 Transaction history and reporting

---

##  Sample Data Included

The project comes with sample data:
- **13 Products** (Arduino, ESP32, Sensors, etc.)
- **5 Categories** (Microcontrollers, Sensors, Power Supplies, Resistors, Capacitors)
- **Sample Transactions** (Stock movements)
- **Admin User** (admin/admin123)

---



### Core Services (1-5):
1. **Amazon EC2** - Host the Django application
2. **Amazon RDS** - PostgreSQL database
3. **Amazon S3** - Product images and static files storage (auto-delete on product removal!)
4. **Amazon SNS** - Email notifications for low stock alerts
5. **Amazon CloudWatch** - Application monitoring and logs


## 📊 Project Structure

```
electronic_inventory/
├── inventory_project/          # Main Django project
│   ├── inventory_project/      # Project settings
│   │   ├── settings.py        # Configuration
│   │   ├── urls.py            # URL routing
│   │   └── wsgi.py            # WSGI config
│   ├── inventory/             # Main app
│   │   ├── models.py          # Database models
│   │   ├── views.py           # View logic
│   │   ├── admin.py           # Admin interface
│   │   ├── urls.py            # App URLs
│   │   ├── templates/         # HTML templates
│   │   ├── static/            # CSS, JS
│   │   └── management/        # Custom commands
│   ├── manage.py              # Django management
│   └── db.sqlite3            # Database file
├── venv/                      # Virtual environment (create this)
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── Documentation files...
```

