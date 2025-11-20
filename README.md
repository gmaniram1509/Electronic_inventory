# Electronic Inventory Management System

A Django-based electronic inventory management system integrated with **10 AWS services** for enterprise-grade cloud deployment.

## 🚀 Quick Start (For First-Time Users)

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

### 🔐 Login Credentials

**URL:** http://localhost:8000/

**Username:** `admin`
**Password:** `admin123`

**Admin Panel:** http://localhost:8000/admin/

> ⚠️ **First time?** See [USER_CREDENTIALS.md](USER_CREDENTIALS.md) for detailed setup instructions.

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

## 🎯 Sample Data Included

The project comes with sample data:
- **13 Products** (Arduino, ESP32, Sensors, etc.)
- **5 Categories** (Microcontrollers, Sensors, Power Supplies, Resistors, Capacitors)
- **Sample Transactions** (Stock movements)
- **Admin User** (admin/admin123)

---

## ☁️ AWS Services Integration (10 Services!)

This system deploys to AWS using **10 cloud services**:

### Core Services (1-5):
1. **Amazon EC2** - Host the Django application
2. **Amazon RDS** - PostgreSQL database
3. **Amazon S3** - Product images and static files storage (auto-delete on product removal!)
4. **Amazon SES** - Email notifications for low stock alerts
5. **Amazon CloudWatch** - Application monitoring and logs

### Advanced Services (6-10):
6. **Amazon SNS** - Real-time push notifications and alerts
7. **Amazon DynamoDB** - Activity and audit logging (NoSQL)
8. **AWS Lambda** - Serverless transaction processing
9. **Amazon ElastiCache** - Redis caching for 50% faster performance
10. **AWS Secrets Manager** - Secure credential storage

> 📖 **Deploy to AWS?**
> - Basic Setup: [AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md)
> - Additional Services: [AWS_ADDITIONAL_SERVICES_SETUP.md](AWS_ADDITIONAL_SERVICES_SETUP.md)
> - Complete Guide: [AWS_10_SERVICES_GUIDE.md](AWS_10_SERVICES_GUIDE.md)

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **USER_CREDENTIALS.md** | Login info and user management |
| **SETUP.md** | Detailed local setup instructions |
| **AWS_SETUP_GUIDE.md** | AWS account and setup (Services 1-5) |
| **AWS_ADDITIONAL_SERVICES_SETUP.md** | Setup additional 5 services (6-10) |
| **AWS_10_SERVICES_GUIDE.md** | Complete 10-service architecture guide |
| **DEPLOYMENT_GUIDE.md** | Deploy to AWS EC2 step-by-step |
| **PROJECT_SETUP_COMPLETE.md** | Project overview and features |

---

## 🛠️ Technology Stack

- **Backend:** Django 4.2.26 (Python 3.11)
- **Database:** SQLite (dev) / PostgreSQL RDS (production)
- **Cache:** Redis (ElastiCache)
- **Frontend:** HTML, CSS, JavaScript
- **Cloud:** AWS (10 services - EC2, RDS, S3, SES, CloudWatch, SNS, DynamoDB, Lambda, ElastiCache, Secrets Manager)
- **Web Server:** Gunicorn + Nginx (production)
- **Serverless:** AWS Lambda for async processing

---

## 📸 Screenshots

### Dashboard
Beautiful, responsive dashboard showing all products, low stock alerts, and recent transactions.

### Admin Panel
Full-featured Django admin for managing products, categories, and transactions.

---

## 🚦 Getting Started Checklist

- [ ] Install Python 3.11
- [ ] Extract project files
- [ ] Create virtual environment
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Run migrations (`python manage.py migrate`)
- [ ] Start server (`python manage.py runserver`)
- [ ] Login with admin/admin123
- [ ] Explore the dashboard!

---

## 🔧 Common Commands

```bash
# Start the development server
python manage.py runserver

# Create a new superuser
python manage.py createsuperuser

# Run database migrations
python manage.py migrate

# Check for low stock and send alerts
python manage.py check_low_stock

# Collect static files
python manage.py collectstatic

# Load sample data
python create_sample_data.py
```

---

## 🆘 Troubleshooting

### "No module named django"
**Solution:** Make sure virtual environment is activated and dependencies are installed
```bash
pip install -r requirements.txt
```

### "No such table" error
**Solution:** Run migrations
```bash
python manage.py migrate
```

### Port 8000 already in use
**Solution:** Use a different port
```bash
python manage.py runserver 8080
```

### Can't login
**Solution:** Check credentials file
- See [USER_CREDENTIALS.md](USER_CREDENTIALS.md)
- Default: admin / admin123

---

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

---

## 🔒 Security Notes

### For Development:
- ✅ Default credentials (admin/admin123) are fine
- ✅ Use on localhost only
- ✅ SQLite database is sufficient

### For Production:
- ⚠️ Change default admin password immediately
- ⚠️ Use strong passwords
- ⚠️ Configure .env file with AWS credentials
- ⚠️ Use PostgreSQL database (RDS)
- ⚠️ Set DEBUG=False
- ⚠️ Configure ALLOWED_HOSTS

---

## 📧 Features in Detail

### Product Management
- Add/Edit/Delete products
- Upload product images (stored in S3 when deployed)
- Attach datasheets
- Track SKU, quantity, pricing
- Set minimum stock levels

### Inventory Tracking
- Real-time stock levels
- Low stock alerts (visual and email)
- Transaction history
- Stock in/out recording

### Email Notifications
- Automatic low stock alerts via AWS SES
- Configurable alert thresholds
- Email sent to admin daily
- Manual alert check available

### Monitoring
- CloudWatch integration for logs
- Error tracking
- Performance metrics
- Application health monitoring

---

## 🌟 What's Next?

1. **Explore the System:** Login and browse the dashboard
2. **Add Products:** Try adding your own inventory items
3. **Test Features:** Create transactions, check alerts
4. **Deploy to AWS:** Follow AWS_SETUP_GUIDE.md to go live
5. **Customize:** Modify templates and styles to your needs

---

## 💰 Cost Information

**Local Development:** FREE
**AWS Deployment:**
- First 12 months (Free Tier): $0-5/month
- After Free Tier: ~$25-30/month

---

## 📞 Support

- Check documentation files in the project
- Read troubleshooting sections
- Review Django documentation: https://docs.djangoproject.com/
- AWS documentation: https://docs.aws.amazon.com/

---

## 📄 License

This project is provided for educational and commercial use.

---

## 🙏 Credits

Built with Django, Python, and AWS services.

**Version:** 1.0
**Last Updated:** November 2025

---

**Happy Inventory Managing! 🎉**
