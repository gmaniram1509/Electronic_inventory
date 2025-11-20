# User Credentials - Electronic Inventory System

## 🔐 Default Login Credentials

### Admin Access (Full Control)

**Username:** `admin`
**Password:** `admin123`

**Access Level:**
- Full admin panel access at `/admin/`
- Dashboard access at `/`
- Can add/edit/delete products, categories, transactions
- Can manage users
- Can upload images
- Full system control

**Login URLs:**
- Admin Panel: http://localhost:8000/admin/
- Dashboard: http://localhost:8000/

---

## 📋 Setup Instructions for Your Friend

### Step 1: Extract the Project
```bash
# Extract the zip file to a location
# Example: C:\Projects\electronic_inventory
```

### Step 2: Install Python 3.11
- Download Python 3.11 from: https://www.python.org/downloads/
- During installation, **CHECK "Add Python to PATH"**
- Verify installation: `py --version` (should show Python 3.11.x)

### Step 3: Create Virtual Environment
```bash
# Navigate to project directory
cd C:\path\to\electronic_inventory

# Create virtual environment
py -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Or for Mac/Linux
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Run Database Migrations
```bash
cd inventory_project
python manage.py migrate
```

### Step 6: Create Superuser (Optional - Create Own Admin)
```bash
# If they want their own admin account
python manage.py createsuperuser

# Follow the prompts:
# Username: (choose a username)
# Email: (their email)
# Password: (choose a password)
```

### Step 7: Load Sample Data (Optional)
```bash
# To populate database with sample products
python create_sample_data.py
```

### Step 8: Run the Server
```bash
python manage.py runserver
```

### Step 9: Access the Application
Open browser and go to:
- **Main Site:** http://localhost:8000/
- **Admin Panel:** http://localhost:8000/admin/

**Login with:**
- Username: `admin`
- Password: `admin123`

---

## 👥 Creating Additional Users

### Via Admin Panel (Recommended)

1. Login to admin panel: http://localhost:8000/admin/
2. Click on **"Users"** under Authentication
3. Click **"Add User"** button
4. Enter:
   - **Username:** (new username)
   - **Password:** (choose password)
5. Click **"Save and continue editing"**
6. Set permissions:
   - **Staff status:** Check this if they should access admin panel
   - **Superuser status:** Check this for full admin rights
   - **Groups/Permissions:** Set specific permissions
7. Fill in optional details (email, first name, last name)
8. Click **"Save"**

### Via Command Line

```bash
# Create a regular user
python manage.py shell

>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user('newuser', 'email@example.com', 'password123')
>>> user.save()
>>> exit()

# Create a staff user (can access admin)
python manage.py shell

>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user('staffuser', 'staff@example.com', 'password123')
>>> user.is_staff = True
>>> user.save()
>>> exit()

# Create a superuser (full admin)
python manage.py createsuperuser
```

---

## 🔑 User Types and Permissions

### 1. Superuser (Full Admin)
- **Default Account:** admin / admin123
- **Can do:** Everything - full control
- **Access:** Admin panel + Dashboard
- **Use for:** System administrators

### 2. Staff User (Limited Admin)
- **Create via:** Admin panel
- **Can do:** Based on assigned permissions
- **Access:** Admin panel (limited) + Dashboard
- **Use for:** Inventory managers, staff

### 3. Regular User
- **Create via:** Admin panel
- **Can do:** Login to dashboard only
- **Access:** Dashboard only (no admin panel)
- **Use for:** View-only users, reporting

---

## 🔒 Security Recommendations

### For Testing/Development:
- ✅ Default credentials (admin/admin123) are fine
- ✅ Use on localhost only

### For Production/Deployment:
- ⚠️ **CHANGE DEFAULT PASSWORD IMMEDIATELY**
- ⚠️ Use strong passwords (12+ characters)
- ⚠️ Create separate user accounts
- ⚠️ Don't share admin credentials
- ⚠️ Enable two-factor authentication (optional)

### Change Admin Password:
```bash
python manage.py changepassword admin
```

Or via admin panel:
1. Login as admin
2. Go to http://localhost:8000/admin/
3. Click "Change password" (top right)
4. Enter current and new password
5. Save

---

## 📝 Quick Reference Card

```
═══════════════════════════════════════════════════
    ELECTRONIC INVENTORY SYSTEM - LOGIN INFO
═══════════════════════════════════════════════════

🌐 URLs:
   Dashboard:    http://localhost:8000/
   Admin Panel:  http://localhost:8000/admin/

🔐 Default Credentials:
   Username:     admin
   Password:     admin123

🚀 Start Server:
   cd inventory_project
   python manage.py runserver

🛑 Stop Server:
   Press Ctrl+C in terminal

📊 Sample Data Included:
   - 13 Products
   - 5 Categories
   - Multiple transactions
   - 2 Low stock items

📧 Admin Email: Can be configured in .env file

═══════════════════════════════════════════════════
   For questions, see README.md or documentation
═══════════════════════════════════════════════════
```

---

## 🎓 First-Time User Guide

### For Your Friend (First Login):

1. **Extract the ZIP file** to a folder
2. **Install Python 3.11** (if not installed)
3. **Open Terminal/Command Prompt** in the project folder
4. **Run these commands:**
   ```bash
   py -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   cd inventory_project
   python manage.py migrate
   python manage.py runserver
   ```
5. **Open browser:** http://localhost:8000/
6. **Login with:** admin / admin123
7. **Explore the system!**

### What Your Friend Can Do:

✅ View all products and inventory
✅ Add new products with images
✅ Create categories
✅ Record stock transactions (in/out)
✅ See low stock alerts
✅ Generate reports
✅ Manage the entire inventory system

---

## 🆘 Troubleshooting

### Issue: "No such table" error
**Solution:** Run migrations
```bash
python manage.py migrate
```

### Issue: "Invalid password" when logging in
**Solution:** Recreate admin user
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username='admin').delete()
>>> User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
>>> exit()
```

### Issue: No products showing
**Solution:** Load sample data
```bash
python create_sample_data.py
```

### Issue: Port 8000 already in use
**Solution:** Use a different port
```bash
python manage.py runserver 8080
# Then access: http://localhost:8080/
```

---

## 📦 What's Included in the ZIP

- ✅ Full Django project
- ✅ All source code
- ✅ Database with sample data
- ✅ Templates and static files
- ✅ Admin user (admin/admin123)
- ✅ 13 sample products
- ✅ Documentation files
- ❌ Virtual environment (your friend must create)
- ❌ AWS credentials (must configure separately)

---

## 🔄 Resetting Everything

If your friend wants to start fresh:

```bash
# Delete database
rm inventory_project/db.sqlite3

# Run migrations
cd inventory_project
python manage.py migrate

# Create new admin
python manage.py createsuperuser

# Load sample data
python create_sample_data.py
```

---

## 📧 Support

If your friend has issues:
1. Check documentation files (README.md, SETUP.md)
2. Ensure Python 3.11 is installed
3. Verify all commands run without errors
4. Check that port 8000 is not in use

**Default Login:** admin / admin123
**Access:** http://localhost:8000/

Good luck! 🚀
